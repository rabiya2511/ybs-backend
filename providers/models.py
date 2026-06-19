from django.db import models
import uuid
from authentication.models import User

class ProviderRole(models.TextChoices):
    CA = 'CA', 'Chartered Accountant'
    DEVELOPER = 'Developer', 'Developer'
    DESIGNER = 'Designer', 'Designer'
    MARKETER = 'Marketer', 'Marketer'
    LEGAL = 'Legal', 'Legal Expert'
    OTHER = 'Other', 'Other'

class AvailabilityStatus(models.TextChoices):
    AVAILABLE = 'Available', 'Available'
    BUSY = 'Busy', 'Busy'
    ON_LEAVE = 'On Leave', 'On Leave'
    INACTIVE = 'Inactive', 'Inactive'

class Provider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')

    role = models.CharField(max_length=20, choices=ProviderRole.choices, default=ProviderRole.OTHER)
    specializations = models.JSONField(default=list)  # list of skill strings
    qualifications = models.TextField(blank=True)

    availability_status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE
    )

    # Bank details for payouts
    bank_account_name = models.CharField(max_length=200, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_ifsc = models.CharField(max_length=20, blank=True)

    # Commission
    commission_type = models.CharField(max_length=10, choices=[
        ('percent', 'Percentage'),
        ('flat', 'Flat Fee'),
    ], default='percent')
    commission_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Performance metrics
    total_orders_completed = models.IntegerField(default=0)
    avg_completion_days = models.FloatField(default=0)
    avg_rating = models.FloatField(default=0)

    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-joined_date']

    def __str__(self):
        return f"{self.user.name} - {self.role}"


class ProviderRating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='ratings')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField()  # 1-5
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider.user.name} - {self.rating} stars"


class ProviderPayout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='payouts')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ], default='Pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.provider.user.name} - ₹{self.amount}"