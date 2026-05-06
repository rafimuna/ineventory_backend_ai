from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import CategorySuggestionSerializer, BatchSuggestionSerializer
from .classifier import classifier
from categories.models import Category
from products.models import Product

class SuggestCategoryView(APIView):
    """একটি প্রোডাক্টের জন্য ক্যাটাগরি সাজেস্ট করে"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CategorySuggestionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_name = serializer.validated_data['product_name']
        description = serializer.validated_data.get('product_description', '')
        
        # Get suggestion
        suggestion = classifier.predict(product_name, description)
        
        # Get all available categories
        categories = Category.objects.values_list('name', flat=True)
        
        return Response({
            'product_name': product_name,
            'suggested_category': suggestion['category'],
            'confidence': suggestion['confidence'],
            'method': suggestion['method'],
            'available_categories': list(categories)
        })

class BatchSuggestCategoriesView(APIView):
    """একসাথে একাধিক প্রোডাক্টের জন্য সাজেশন (API ব্যবহার কমাতে)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = BatchSuggestionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        products = serializer.validated_data['products']
        suggestions = classifier.suggest_for_multiple(products)
        
        results = []
        for product, suggestion in zip(products, suggestions):
            results.append({
                'product_name': product.get('name', ''),
                'suggested_category': suggestion['category'],
                'confidence': suggestion['confidence'],
                'method': suggestion['method']
            })
        
        return Response({'suggestions': results})

class TrainModelView(APIView):
    """ম্যানুয়ালি মডেল রিট্রেইন করার জন্য"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Check if user is admin
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admin can retrain the model'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            classifier.train()
            return Response({'message': 'Model retrained successfully!'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AcceptSuggestionView(APIView):
    """ইউজার সাজেশন accept করলে লগ রাখে (ভবিষ্যতে ট্রেইনিং-এর জন্য)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        product_id = request.data.get('product_id')
        accepted_category = request.data.get('accepted_category')
        
        try:
            product = Product.objects.get(id=product_id)
            category = Category.objects.get(name=accepted_category)
            
            # Update product category
            product.category = category
            product.save()
            
            # Log the acceptance
            from .models import CategorySuggestionLog
            CategorySuggestionLog.objects.create(
                product_name=product.name,
                suggested_category=accepted_category,
                confidence=request.data.get('confidence', 0),
                was_accepted=True
            )
            
            return Response({'message': 'Category updated successfully!'})
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=404)