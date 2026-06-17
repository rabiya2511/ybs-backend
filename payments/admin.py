from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'order', 'client',
        'total_amount', 'payment_method', 'status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'order__order_number', 'client__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(Payment, PaymentAdmin)