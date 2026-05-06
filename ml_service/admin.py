from django.contrib import admin
from .models import CategorySuggestionLog

@admin.register(CategorySuggestionLog)
class CategorySuggestionLogAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'suggested_category', 'confidence', 'was_accepted', 'created_at')
    list_filter = ('was_accepted', 'created_at')
    search_fields = ('product_name', 'suggested_category')
    readonly_fields = ('created_at',)