from django.contrib import admin
from .models import Order, OrderDocument

class OrderDocumentInline(admin.TabularInline):
    model = OrderDocument
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'client', 'service',
        'package', 'total_paid', 'status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'client__email', 'client__name']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderDocumentInline]

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'client', 'service', 'package', 'provider')
        }),
        ('Pricing', {
            'fields': ('base_amount', 'gst_amount', 'discount', 'total_paid')
        }),
        ('Payment', {
            'fields': ('payment_method', 'razorpay_order_id', 'razorpay_payment_id')
        }),
        ('Status & Milestones', {
            'fields': ('status', 'milestones', 'expected_completion_date')
        }),
        ('Business Details', {
            'fields': ('business_name', 'business_type', 'business_category', 'number_of_directors')
        }),
        ('Notes', {
            'fields': ('internal_notes',)
        }),
    )

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDocument)