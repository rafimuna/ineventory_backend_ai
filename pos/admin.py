from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import PaymentMethod, Order, OrderItem


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """পেমেন্ট মাধ্যম অ্যাডমিন"""
    list_display = ['id', 'name', 'is_active']
    list_editable = ['is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']


class OrderItemInline(admin.TabularInline):
    """অর্ডারের ভিতরে আইটেম দেখানোর জন্য"""
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'total']
    fields = ['product', 'quantity', 'price', 'total']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """অর্ডার অ্যাডমিন"""
    list_display = [
        'order_number', 'cashier_info', 'order_date', 'total_amount',
        'discount', 'grand_total', 'payment_method_info', 'status_badge', 
        'view_order_link'
    ]
    list_filter = ['status', 'payment_method', 'order_date', 'cashier']
    search_fields = ['order_number', 'cashier__username', 'cashier__email']
    readonly_fields = ['order_number', 'order_date', 'total_amount', 'grand_total']
    inlines = [OrderItemInline]
    date_hierarchy = 'order_date'
    
    fieldsets = (
        ('অর্ডার তথ্য', {
            'fields': ('order_number', 'cashier', 'order_date', 'status')
        }),
        ('আর্থিক তথ্য', {
            'fields': ('total_amount', 'discount', 'tax', 'grand_total')
        }),
        ('পেমেন্ট তথ্য', {
            'fields': ('payment_method',)
        }),
        ('অতিরিক্ত তথ্য', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    def cashier_info(self, obj):
        """ক্যাশিয়ারের তথ্য দেখানো"""
        return format_html(
            '<strong>{}</strong><br/><span style="color:gray;">{}</span>',
            obj.cashier.username,
            obj.cashier.email
        )
    cashier_info.short_description = 'ক্যাশিয়ার'
    
    def payment_method_info(self, obj):
        """পেমেন্ট মাধ্যম দেখানো"""
        if obj.payment_method:
            return obj.payment_method.name
        return '-'
    payment_method_info.short_description = 'পেমেন্ট মাধ্যম'
    
    def status_badge(self, obj):
        """স্ট্যাটাস ব্যাজ দেখানো"""
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'cancelled': 'red',
            'refunded': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'স্ট্যাটাস'
    
    def view_order_link(self, obj):
        """অর্ডার ডিটেইল লিংক"""
        url = reverse('admin:pos_order_change', args=[obj.id])
        return format_html('<a href="{}" target="_blank">🔍 বিস্তারিত দেখুন</a>', url)
    view_order_link.short_description = 'অ্যাকশন'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cashier', 'payment_method')
    
    actions = ['mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_completed(self, request, queryset):
        """একাধিক অর্ডার কমপ্লিটেড মার্ক করা"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} টি অর্ডার কমপ্লিটেড করা হয়েছে।')
    mark_as_completed.short_description = 'সিলেক্টেড অর্ডার কমপ্লিটেড করুন'
    
    def mark_as_cancelled(self, request, queryset):
        """একাধিক অর্ডার ক্যান্সেল করা"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} টি অর্ডার ক্যান্সেল করা হয়েছে।')
    mark_as_cancelled.short_description = 'সিলেক্টেড অর্ডার ক্যান্সেল করুন'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """অর্ডার আইটেম অ্যাডমিন"""
    list_display = ['order', 'product', 'quantity', 'price', 'total']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['total']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False