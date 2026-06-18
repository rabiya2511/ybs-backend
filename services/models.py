from django.db import models
import uuid

class Category(models.TextChoices):
    LEGAL = 'Legal', 'Legal'
    DESIGN = 'Design', 'Design'
    TECH = 'Tech', 'Tech'
    FINANCE = 'Finance', 'Finance'
    FOOD_ISO = 'Food & ISO', 'Food & ISO'

class BillingPeriod(models.TextChoices):
    ONE_TIME = 'one_time', 'One Time'
    MONTHLY = 'monthly', 'Monthly'
    YEARLY = 'yearly', 'Yearly'

class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=Category.choices)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🏢')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)  # ← add this line
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class Package(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period = models.CharField(max_length=20, choices=BillingPeriod.choices, default=BillingPeriod.ONE_TIME)
    features = models.JSONField(default=list)  # list of feature strings
    is_recommended = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)  # for drag-drop ordering
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.service.name} - {self.name}"