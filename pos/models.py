from django.db import models
from django.conf import settings
from products.models import Product
from decimal import Decimal

class PaymentMethod(models.Model):
    """পেমেন্টের মাধ্যম যেমন - নগদ, বিকাশ, ভিসা কার্ড"""
    name = models.CharField(max_length=50)  # e.g., "Cash", "bKash", "Visa Card"
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    """মূল অর্ডার টেবিল"""
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),  # Payment received, stock deducted
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    order_number = models.CharField(max_length=20, unique=True)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    """অর্ডারের প্রতিটি আইটেম"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot of price at sale time
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.price * Decimal(self.quantity)
        super().save(*args, **kwargs)