from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from .models import PaymentMethod, Order, OrderItem
from .serializers import (
    PaymentMethodSerializer, OrderListSerializer, OrderDetailSerializer,
    OrderCreateSerializer, OrderUpdateSerializer
)
from products.models import Product
from inventory.models import StockLog
import random
import string


class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """পেমেন্ট মাধ্যম - শুধু পড়ার জন্য"""
    permission_classes = [IsAuthenticated]
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """অর্ডার ম্যানেজমেন্ট"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Order.objects.select_related('cashier', 'payment_method')
        
        # ফিল্টারিং
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        date_filter = self.request.query_params.get('date')
        if date_filter:
            queryset = queryset.filter(order_date__date=date_filter)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(order_number__icontains=search)
        
        return queryset.order_by('-order_date')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return OrderUpdateSerializer
        return OrderListSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(cashier=request.user)
        
        # OrderDetailSerializer দিয়ে রেসপন্স পাঠাও
        detail_serializer = OrderDetailSerializer(order)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """অর্ডারের স্ট্যাটাস আপডেট"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.ORDER_STATUS):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save()
        
        return Response({'status': order.status, 'message': f'Order {new_status}'})


class DailyReportViewSet(viewsets.ViewSet):
    """দৈনিক সেলস রিপোর্ট"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        date = request.query_params.get('date', timezone.now().date())
        
        orders = Order.objects.filter(
            order_date__date=date,
            status='completed'
        )
        
        total_orders = orders.count()
        total_sales = orders.aggregate(total=models.Sum('grand_total'))['total'] or 0
        total_items = OrderItem.objects.filter(order__in=orders).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        
        return Response({
            'date': date,
            'total_orders': total_orders,
            'total_sales': total_sales,
            'total_items_sold': total_items,
            'average_order_value': total_sales / total_orders if total_orders > 0 else 0
        })