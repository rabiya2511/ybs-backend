from django.db import models
import uuid
from authentication.models import User
from services.models import Service, Package

class OrderStatus(models.TextChoices):
    QUEUED = 'Queued', 'Queued'
    ACTIVE = 'Active', 'Active'
    REVIEW = 'Review', 'Review'
    DONE = 'Done', 'Done'
    ON_HOLD = 'On Hold', 'On Hold'
    CANCELLED = 'Cancelled', 'Cancelled'

class PaymentMethod(models.TextChoices):
    UPI = 'UPI', 'UPI'
    CARD = 'Card', 'Card'
    NET_BANKING = 'NetBanking', 'NetBanking'

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, blank=True)

    # Relations
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, related_name='orders')
    provider = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_orders'
    )

    # Pricing
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.UPI
    )
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.QUEUED
    )

    # Milestones stored as JSON
    milestones = models.JSONField(default=list)

    # Business details from checkout
    business_name = models.CharField(max_length=200, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    business_category = models.CharField(max_length=100, blank=True)
    number_of_directors = models.CharField(max_length=10, blank=True)

    # Notes
    internal_notes = models.TextField(blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_number} - {self.client.name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            last = Order.objects.order_by('-created_at').first()
            if last and last.order_number:
                try:
                    num = int(last.order_number.split('-')[1]) + 1
                except:
                    num = 1
            else:
                num = 1
            self.order_number = f"YBS-{str(num).zfill(4)}"
        super().save(*args, **kwargs)


class OrderDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='order_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_deliverable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.name}"