import uuid
from django.db import models

class GeneralSettings(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name     = models.CharField(max_length=200, default='YBS')
    company_email    = models.EmailField(default='info@ybs.in')
    company_phone    = models.CharField(max_length=20, blank=True)
    company_address  = models.TextField(blank=True)
    company_website  = models.URLField(blank=True)
    gst_number       = models.CharField(max_length=20, blank=True)
    pan_number       = models.CharField(max_length=20, blank=True)
    timezone         = models.CharField(max_length=50, default='Asia/Kolkata')
    currency         = models.CharField(max_length=10, default='INR')
    date_format      = models.CharField(max_length=20, default='DD/MM/YYYY')
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'General Settings'

    def __str__(self):
        return self.company_name


class BrandingSettings(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logo             = models.ImageField(upload_to='branding/', null=True, blank=True)
    favicon          = models.ImageField(upload_to='branding/', null=True, blank=True)
    primary_color    = models.CharField(max_length=10, default='#0B1E3D')
    secondary_color  = models.CharField(max_length=10, default='#C9A84C')
    company_tagline  = models.CharField(max_length=255, blank=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Branding Settings'

    def __str__(self):
        return 'Branding Settings'


class EmailSettings(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    smtp_host        = models.CharField(max_length=200, blank=True)
    smtp_port        = models.IntegerField(default=587)
    smtp_username    = models.CharField(max_length=200, blank=True)
    smtp_password    = models.CharField(max_length=200, blank=True)
    use_tls          = models.BooleanField(default=True)
    from_email       = models.EmailField(default='noreply@ybs.in')
    from_name        = models.CharField(max_length=100, default='YBS')
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Email Settings'

    def __str__(self):
        return 'Email Settings'


class PaymentSettings(models.Model):
    id                    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    razorpay_key_id       = models.CharField(max_length=200, blank=True)
    razorpay_key_secret   = models.CharField(max_length=200, blank=True)
    razorpay_enabled      = models.BooleanField(default=False)
    stripe_publishable_key = models.CharField(max_length=200, blank=True)
    stripe_secret_key     = models.CharField(max_length=200, blank=True)
    stripe_enabled        = models.BooleanField(default=False)
    gst_percentage        = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    updated_at            = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Settings'

    def __str__(self):
        return 'Payment Settings'