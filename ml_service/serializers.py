from rest_framework import serializers

class CategorySuggestionSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    product_description = serializers.CharField(required=False, allow_blank=True)
    suggested_category = serializers.CharField(read_only=True)
    confidence = serializers.FloatField(read_only=True)
    method = serializers.CharField(read_only=True)

class BatchSuggestionSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of products with 'name' and optional 'description'"
    )