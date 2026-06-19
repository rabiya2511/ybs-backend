import uuid
from django.db import models
from authentication.models import User

class ReferralStatus(models.TextChoices):
    PENDING   = 'Pending', 'Pending'
    CONVERTED = 'Converted', 'Converted'
    EXPIRED   = 'Expired', 'Expired'

class Referral(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referred_by   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_by_user')
    referred_email = models.EmailField()
    status        = models.CharField(max_length=20, choices=ReferralStatus.choices, default=ReferralStatus.PENDING)
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    reward_claimed = models.BooleanField(default=False)
    converted_at  = models.DateTimeField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.referred_by.name} → {self.referred_email} ({self.status})"


class ReferralReward(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_rewards')
    referral    = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='rewards')
    amount      = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    is_claimed  = models.BooleanField(default=False)
    claimed_at  = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - ₹{self.amount} ({'Claimed' if self.is_claimed else 'Pending'})"