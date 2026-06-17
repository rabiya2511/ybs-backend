from django.contrib import admin
from .models import Invoice, Bill, Expense

class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'client', 'total',
        'status', 'due_date', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['invoice_number', 'client__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

class BillAdmin(admin.ModelAdmin):
    list_display = [
        'bill_number', 'vendor_name', 'category',
        'amount', 'due_date', 'status'
    ]
    list_filter = ['status', 'category']
    search_fields = ['bill_number', 'vendor_name']
    ordering = ['-created_at']

class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        'category', 'description', 'amount',
        'gst_applicable', 'paid_by', 'date'
    ]
    list_filter = ['category', 'gst_applicable']
    ordering = ['-date']

admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(Expense, ExpenseAdmin)