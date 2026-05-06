from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StockLog
from .serializers import StockLogSerializer
from products.models import Product
from .forecast import forecast_demand

class StockAdjustView(generics.CreateAPIView):
    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        quantity_change = int(request.data.get('quantity_change', 0))
        reason = request.data.get('reason')

        if quantity_change == 0:
            return Response({'error': 'Quantity change cannot be zero'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        # Update product quantity
        new_quantity = product.quantity + quantity_change
        if new_quantity < 0:
            return Response({'error': 'Insufficient stock'}, status=400)
        product.quantity = new_quantity
        product.save()

        # Create log
        log = StockLog.objects.create(
            product=product,
            quantity_change=quantity_change,
            reason=reason,
            created_by=request.user
        )
        serializer = self.get_serializer(log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class StockLogListView(generics.ListAPIView):
    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = StockLog.objects.select_related('product', 'created_by').all()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset.order_by('-timestamp')

class DemandForecastView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id):
        result = forecast_demand(product_id)
        return Response(result)