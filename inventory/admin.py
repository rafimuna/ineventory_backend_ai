from django.contrib import admin
from .models import StockLog

@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_change', 'reason', 'created_by', 'timestamp')
    list_filter = ('reason', 'timestamp', 'product')
    search_fields = ('product__name', 'reason')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_change_permission(self, request, obj=None):
        # StockLog এডিট করতে দেবে না (শুধু ভিউ)
        return False