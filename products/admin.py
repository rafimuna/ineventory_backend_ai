from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'quantity', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'sku')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('price', 'quantity')  # তালিকা থেকেই এডিট করা যাবে
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'quantity')
        }),
        ('Images', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )