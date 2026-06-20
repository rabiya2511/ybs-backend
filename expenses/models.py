import uuid
from django.db import models
from authentication.models import User

class ExpenseCategory(models.TextChoices):
    OFFICE       = 'Office', 'Office'
    TRAVEL       = 'Travel', 'Travel'
    SOFTWARE     = 'Software', 'Software'
    MARKETING    = 'Marketing', 'Marketing'
    SALARIES     = 'Salaries', 'Salaries'
    UTILITIES    = 'Utilities', 'Utilities'
    RENT         = 'Rent', 'Rent'
    MISCELLANEOUS = 'Miscellaneous', 'Miscellaneous'

class ExpenseStatus(models.TextChoices):
    PENDING  = 'Pending', 'Pending'
    APPROVED = 'Approved', 'Approved'
    REJECTED = 'Rejected', 'Rejected'
    PAID     = 'Paid', 'Paid'

class Expense(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    category    = models.CharField(max_length=20, choices=ExpenseCategory.choices, default=ExpenseCategory.MISCELLANEOUS)
    status      = models.CharField(max_length=20, choices=ExpenseStatus.choices, default=ExpenseStatus.PENDING)
    expense_date = models.DateField()
    receipt     = models.FileField(upload_to='expense_receipts/', null=True, blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expenses')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    approved_at = models.DateTimeField(null=True, blank=True)
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"