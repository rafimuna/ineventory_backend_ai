from django.db import models
from products.models import Product
from users.models import User

class StockLog(models.Model):
    REASON_CHOICES = (
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_logs')
    quantity_change = models.IntegerField()  # positive for increase, negative for decrease
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} : {self.quantity_change}"