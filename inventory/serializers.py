from rest_framework import serializers
from .models import StockLog
from products.serializers import ProductSerializer

class StockLogSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = StockLog
        fields = '__all__'
        read_only_fields = ('timestamp',)