import uuid
from django.db import models
from authentication.models import User

class BillStatus(models.TextChoices):
    PENDING  = 'Pending', 'Pending'
    APPROVED = 'Approved', 'Approved'
    PAID     = 'Paid', 'Paid'
    OVERDUE  = 'Overdue', 'Overdue'
    REJECTED = 'Rejected', 'Rejected'

class BillCategory(models.TextChoices):
    VENDOR      = 'Vendor', 'Vendor'
    UTILITY     = 'Utility', 'Utility'
    RENT        = 'Rent', 'Rent'
    SALARY      = 'Salary', 'Salary'
    SOFTWARE    = 'Software', 'Software'
    MARKETING   = 'Marketing', 'Marketing'
    MISCELLANEOUS = 'Miscellaneous', 'Miscellaneous'

class Bill(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_number  = models.CharField(max_length=20, unique=True, blank=True)
    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    gst_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category     = models.CharField(max_length=20, choices=BillCategory.choices, default=BillCategory.MISCELLANEOUS)
    status       = models.CharField(max_length=20, choices=BillStatus.choices, default=BillStatus.PENDING)
    vendor_name  = models.CharField(max_length=200, blank=True)
    vendor_email = models.EmailField(blank=True)
    bill_date    = models.DateField()
    due_date     = models.DateField(null=True, blank=True)
    paid_at      = models.DateTimeField(null=True, blank=True)
    attachment   = models.FileField(upload_to='bills/', null=True, blank=True)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bills')
    approved_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bills')
    approved_at  = models.DateTimeField(null=True, blank=True)
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bill_number} - {self.title}"

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
        if not self.total_amount:
            self.total_amount = self.amount + self.gst_amount
        super().save(*args, **kwargs)