from django.contrib import admin
from .models import Payment, Coupon, CouponUsage

class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'order', 'client',
        'total_amount', 'payment_method', 'status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'order__order_number', 'client__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_type', 'discount_value',
        'usage_limit', 'used_count', 'is_active', 'expires_at'
    ]
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(CouponUsage)