from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from decimal import Decimal
from products.models import Product
from inventory.models import StockLog

class POSCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        cashier = request.user
        items_data = data.get('items')
        payment_method = data.get('payment_method')
        discount = Decimal(data.get('discount', 0))
        notes = data.get('notes', '')

        # 1. ভ্যালিডেশন ও স্টক চেক
        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            if product.quantity < item['quantity']: # StockLog ব্যবহার করে ইনভেন্টরি চেক
                return Response({"error": f"{product.name} এর জন্য স্টক অপর্যাপ্ত"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. অর্ডার অবজেক্ট তৈরি ও সেভ
        order = Order.objects.create(
            order_number=self.generate_order_number(),
            cashier=cashier,
            discount=discount,
            payment_method_id=payment_method,
            notes=notes,
            status='pending'
        )

        # 3. অর্ডার আইটেম যোগ করা ও স্টক হ্রাস করা
        total, grand_total = 0, 0
        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            price = product.price
            quantity = item['quantity']
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

            # ইনভেন্টরি আপডেট (StockLog তৈরি)
            StockLog.objects.create(
                product=product,
                quantity_change=-quantity,  # এটাই মূল কৌশল
                reason='sale',
                created_by=cashier
            )
            total += price * quantity

        grand_total = total - discount
        order.total_amount = total
        order.grand_total = grand_total
        order.status = 'completed'
        order.save()

        return Response({"message": "Order completed!", "order_id": order.id}, status=status.HTTP_201_CREATED)

    def generate_order_number(self):
        # একটি ইউনিক অর্ডার নম্বর জেনারেট করুন (যেমন, INv/2025/0001 ফরম্যাটে)
        import time
        return f"ORD-{int(time.time())}"