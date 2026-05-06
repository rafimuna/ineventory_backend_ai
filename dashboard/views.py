from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from products.models import Product
from inventory.models import StockLog

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(quantity__lt=10).count()
        total_stock_value = sum(p.price * p.quantity for p in Product.objects.all())
        recent_activities = StockLog.objects.select_related('product').order_by('-timestamp')[:10]

        recent_data = [
            {
                'product': log.product.name,
                'change': log.quantity_change,
                'reason': log.reason,
                'timestamp': log.timestamp
            }
            for log in recent_activities
        ]

        return Response({
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'total_stock_value': total_stock_value,
            'recent_activities': recent_data
        })