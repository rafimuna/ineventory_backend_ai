from rest_framework import serializers
from .models import PaymentMethod, Order, OrderItem
from products.models import Product
from users.models import User

class PaymentMethodSerializer(serializers.ModelSerializer):
    """পেমেন্ট মাধ্যম সিরিয়ালাইজার"""
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'is_active']
        read_only_fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    """অর্ডার আইটেম সিরিয়ালাইজার"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'product_sku', 
                  'product_price', 'quantity', 'price', 'total']
        read_only_fields = ['id', 'total']


class OrderListSerializer(serializers.ModelSerializer):
    """অর্ডার লিস্ট দেখানোর জন্য সিরিয়ালাইজার (লাইটওয়েট)"""
    cashier_name = serializers.CharField(source='cashier.username', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'cashier_name', 'order_date', 
                  'grand_total', 'payment_method_name', 'status', 'item_count']
    
    def get_item_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """অর্ডার ডিটেইল দেখানোর জন্য সিরিয়ালাইজার (সম্পূর্ণ)"""
    cashier_details = serializers.SerializerMethodField()
    payment_method_details = PaymentMethodSerializer(source='payment_method', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'cashier_details', 'order_date', 
                  'total_amount', 'discount', 'tax', 'grand_total', 
                  'payment_method_details', 'status', 'notes', 'items']
    
    def get_cashier_details(self, obj):
        return {
            'id': obj.cashier.id,
            'username': obj.cashier.username,
            'email': obj.cashier.email,
            'role': obj.cashier.role
        }


class OrderCreateSerializer(serializers.ModelSerializer):
    """নতুন অর্ডার তৈরি করার জন্য সিরিয়ালাইজার"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text='আইটেমের তালিকা: [{"product_id": 1, "quantity": 2}, ...]'
    )
    
    class Meta:
        model = Order
        fields = ['discount', 'tax', 'payment_method', 'notes', 'items']
    
    def validate_items(self, value):
        """আইটেম ভ্যালিডেশন"""
        if not value:
            raise serializers.ValidationError("কমপক্ষে একটি আইটেম প্রয়োজন")
        
        for item in value:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            
            if not product_id:
                raise serializers.ValidationError("প্রতিটি আইটেমে product_id প্রয়োজন")
            
            if quantity <= 0:
                raise serializers.ValidationError("পরিমাণ ০ এর বেশি হতে হবে")
            
            try:
                product = Product.objects.get(id=product_id)
                if product.quantity < quantity:
                    raise serializers.ValidationError(
                        f"{product.name} এর স্টক অপর্যাপ্ত। স্টক আছে: {product.quantity}"
                    )
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"product_id {product_id} পাওয়া যায়নি")
        
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        cashier = self.context['request'].user
        
        # অর্ডার নম্বর জেনারেট করুন
        import time
        order_number = f"ORD-{int(time.time())}-{cashier.id}"
        
        # অর্ডার তৈরি
        order = Order.objects.create(
            order_number=order_number,
            cashier=cashier,
            discount=validated_data.get('discount', 0),
            tax=validated_data.get('tax', 0),
            payment_method=validated_data.get('payment_method'),
            notes=validated_data.get('notes', ''),
            status='pending'
        )
        
        total_amount = 0
        
        # অর্ডার আইটেম তৈরি
        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            price = product.price
            quantity = item['quantity']
            
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            total_amount += order_item.total
            
            # স্টক হ্রাস (ইনভেন্টরি লগ তৈরি)
            from inventory.models import StockLog
            StockLog.objects.create(
                product=product,
                quantity_change=-quantity,
                reason='sale',
                created_by=cashier
            )
        
        # অর্ডার আপডেট
        order.total_amount = total_amount
        order.grand_total = total_amount - order.discount + order.tax
        order.status = 'completed'
        order.save()
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """অর্ডার স্ট্যাটাস আপডেট করার জন্য সিরিয়ালাইজার"""
    class Meta:
        model = Order
        fields = ['status', 'notes']
    
    def validate_status(self, value):
        valid_statuses = ['pending', 'completed', 'cancelled', 'refunded']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"স্ট্যাটাস হতে হবে: {', '.join(valid_statuses)}")
        return value


class POSCartItemSerializer(serializers.Serializer):
    """POS কার্টের জন্য সিরিয়ালাইজার"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    product_name = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            self.context['product'] = product
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("পণ্যটি পাওয়া যায়নি")
    
    def validate(self, data):
        product = self.context.get('product')
        if product and product.quantity < data['quantity']:
            raise serializers.ValidationError(
                f"{product.name} এর স্টক অপর্যাপ্ত। স্টক আছে: {product.quantity}"
            )
        return data


class DailySalesReportSerializer(serializers.Serializer):
    """দৈনিক সেলস রিপোর্ট সিরিয়ালাইজার"""
    date = serializers.DateField()
    total_orders = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_items_sold = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    cashier_breakdown = serializers.ListField(child=serializers.DictField(), required=False)
    payment_method_breakdown = serializers.ListField(child=serializers.DictField(), required=False)