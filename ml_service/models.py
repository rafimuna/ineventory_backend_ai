from django.db import models

class CategorySuggestionLog(models.Model):
    """লগ রাখবে কখন কোন প্রোডাক্টের জন্য কি সাজেস্ট করেছিল"""
    product_name = models.CharField(max_length=200)
    suggested_category = models.CharField(max_length=100)
    confidence = models.FloatField()
    was_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product_name} -> {self.suggested_category} ({self.confidence:.2f})"