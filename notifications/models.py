from django.db import models
import uuid
from authentication.models import User

class NotificationType(models.TextChoices):
    ORDER_UPDATE = 'ORDER_UPDATE', 'Order Update'
    MILESTONE = 'MILESTONE', 'Milestone Update'
    PAYMENT = 'PAYMENT', 'Payment'
    COMPLIANCE = 'COMPLIANCE', 'Compliance Deadline'
    DOCUMENT = 'DOCUMENT', 'Document Request'
    REFERRAL = 'REFERRAL', 'Referral'
    PROMOTIONAL = 'PROMOTIONAL', 'Promotional'
    GENERAL = 'GENERAL', 'General'

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    body = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Optional link to related object
    related_order_id = models.UUIDField(null=True, blank=True)
    related_invoice_id = models.UUIDField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class ComplianceDeadline(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deadlines')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    due_date = models.DateField()
    category = models.CharField(max_length=100, choices=[
        ('GST', 'GST Return'),
        ('TDS', 'TDS Return'),
        ('ROC', 'ROC Filing'),
        ('PF', 'PF/ESI'),
        ('ITR', 'Income Tax Return'),
        ('OTHER', 'Other'),
    ], default='OTHER')
    is_completed = models.BooleanField(default=False)
    notified_30 = models.BooleanField(default=False)
    notified_7 = models.BooleanField(default=False)
    notified_1 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} - {self.due_date}"