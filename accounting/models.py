from django.db import models
import uuid
from authentication.models import User
from orders.models import Order

class InvoiceStatus(models.TextChoices):
    DRAFT = 'Draft', 'Draft'
    SENT = 'Sent', 'Sent'
    DUE = 'Due', 'Due'
    OVERDUE = 'Overdue', 'Overdue'
    PAID = 'Paid', 'Paid'
    CANCELLED = 'Cancelled', 'Cancelled'

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=20, unique=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')

    # Line items stored as JSON
    line_items = models.JSONField(default=list)

    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Dates
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()

    # Status
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number


class Bill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_number = models.CharField(max_length=20, unique=True, blank=True)
    vendor_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
    ], default='Pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bill_number} - {self.vendor_name}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            last = Bill.objects.order_by('-created_at').first()
            if last and last.bill_number:
                try:
                    num = int(last.bill_number.split('-')[1]) + 1
                except:
                    num = 1
            else:
                num = 1
            self.bill_number = f"BILL-{str(num).zfill(4)}"
        super().save(*args, **kwargs)


class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    category = models.CharField(max_length=100, choices=[
        ('Travel', 'Travel'),
        ('Meals', 'Meals'),
        ('Office Supplies', 'Office Supplies'),
        ('Utilities', 'Utilities'),
        ('Marketing', 'Marketing'),
        ('Miscellaneous', 'Miscellaneous'),
    ])
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gst_applicable = models.BooleanField(default=False)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_by = models.CharField(max_length=100)
    receipt = models.FileField(upload_to='expense_receipts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.category} - ₹{self.amount}"