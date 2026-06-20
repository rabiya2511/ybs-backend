from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import GeneralSettings, BrandingSettings, EmailSettings, PaymentSettings
from authentication.permissions import IsAdminOrSuperAdmin


def get_or_create_singleton(model):
    obj = model.objects.first()
    if not obj:
        obj = model.objects.create()
    return obj


# ══════════════════════════════════════════════
# GET /api/settings/general/
# PUT /api/settings/general/
# ══════════════════════════════════════════════
class GeneralSettingsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        settings = get_or_create_singleton(GeneralSettings)
        return Response({
            'success': True,
            'data': {
                'id': str(settings.id),
                'company_name': settings.company_name,
                'company_email': settings.company_email,
                'company_phone': settings.company_phone,
                'company_address': settings.company_address,
                'company_website': settings.company_website,
                'gst_number': settings.gst_number,
                'pan_number': settings.pan_number,
                'timezone': settings.timezone,
                'currency': settings.currency,
                'date_format': settings.date_format,
                'updated_at': settings.updated_at,
            }
        })

    def put(self, request):
        settings = get_or_create_singleton(GeneralSettings)
        fields = [
            'company_name', 'company_email', 'company_phone',
            'company_address', 'company_website', 'gst_number',
            'pan_number', 'timezone', 'currency', 'date_format'
        ]
        for field in fields:
            if field in request.data:
                setattr(settings, field, request.data[field])
        settings.save()

        return Response({
            'success': True,
            'message': 'General settings updated successfully.',
            'data': {
                'company_name': settings.company_name,
                'company_email': settings.company_email,
                'company_phone': settings.company_phone,
                'company_address': settings.company_address,
                'company_website': settings.company_website,
                'gst_number': settings.gst_number,
                'pan_number': settings.pan_number,
                'timezone': settings.timezone,
                'currency': settings.currency,
                'date_format': settings.date_format,
            }
        })


# ══════════════════════════════════════════════
# GET /api/settings/branding/
# PUT /api/settings/branding/
# ══════════════════════════════════════════════
class BrandingSettingsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        settings = get_or_create_singleton(BrandingSettings)
        return Response({
            'success': True,
            'data': {
                'id': str(settings.id),
                'logo': request.build_absolute_uri(settings.logo.url) if settings.logo else None,
                'favicon': request.build_absolute_uri(settings.favicon.url) if settings.favicon else None,
                'primary_color': settings.primary_color,
                'secondary_color': settings.secondary_color,
                'company_tagline': settings.company_tagline,
                'updated_at': settings.updated_at,
            }
        })

    def put(self, request):
        settings = get_or_create_singleton(BrandingSettings)

        if 'primary_color' in request.data:
            settings.primary_color = request.data['primary_color']
        if 'secondary_color' in request.data:
            settings.secondary_color = request.data['secondary_color']
        if 'company_tagline' in request.data:
            settings.company_tagline = request.data['company_tagline']
        if 'logo' in request.FILES:
            settings.logo = request.FILES['logo']
        if 'favicon' in request.FILES:
            settings.favicon = request.FILES['favicon']

        settings.save()

        return Response({
            'success': True,
            'message': 'Branding settings updated successfully.',
            'data': {
                'primary_color': settings.primary_color,
                'secondary_color': settings.secondary_color,
                'company_tagline': settings.company_tagline,
                'logo': request.build_absolute_uri(settings.logo.url) if settings.logo else None,
                'favicon': request.build_absolute_uri(settings.favicon.url) if settings.favicon else None,
            }
        })


# ══════════════════════════════════════════════
# GET /api/settings/email/
# PUT /api/settings/email/
# ══════════════════════════════════════════════
class EmailSettingsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        settings = get_or_create_singleton(EmailSettings)
        return Response({
            'success': True,
            'data': {
                'id': str(settings.id),
                'smtp_host': settings.smtp_host,
                'smtp_port': settings.smtp_port,
                'smtp_username': settings.smtp_username,
                'use_tls': settings.use_tls,
                'from_email': settings.from_email,
                'from_name': settings.from_name,
                'updated_at': settings.updated_at,
            }
        })

    def put(self, request):
        settings = get_or_create_singleton(EmailSettings)
        fields = [
            'smtp_host', 'smtp_port', 'smtp_username',
            'smtp_password', 'use_tls', 'from_email', 'from_name'
        ]
        for field in fields:
            if field in request.data:
                setattr(settings, field, request.data[field])
        settings.save()

        return Response({
            'success': True,
            'message': 'Email settings updated successfully.',
            'data': {
                'smtp_host': settings.smtp_host,
                'smtp_port': settings.smtp_port,
                'smtp_username': settings.smtp_username,
                'use_tls': settings.use_tls,
                'from_email': settings.from_email,
                'from_name': settings.from_name,
            }
        })


# ══════════════════════════════════════════════
# GET /api/settings/payment/
# PUT /api/settings/payment/
# ══════════════════════════════════════════════
class PaymentSettingsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        settings = get_or_create_singleton(PaymentSettings)
        return Response({
            'success': True,
            'data': {
                'id': str(settings.id),
                'razorpay_key_id': settings.razorpay_key_id,
                'razorpay_enabled': settings.razorpay_enabled,
                'stripe_publishable_key': settings.stripe_publishable_key,
                'stripe_enabled': settings.stripe_enabled,
                'gst_percentage': str(settings.gst_percentage),
                'updated_at': settings.updated_at,
            }
        })

    def put(self, request):
        settings = get_or_create_singleton(PaymentSettings)
        fields = [
            'razorpay_key_id', 'razorpay_key_secret',
            'razorpay_enabled', 'stripe_publishable_key',
            'stripe_secret_key', 'stripe_enabled', 'gst_percentage'
        ]
        for field in fields:
            if field in request.data:
                setattr(settings, field, request.data[field])
        settings.save()

        return Response({
            'success': True,
            'message': 'Payment settings updated successfully.',
            'data': {
                'razorpay_key_id': settings.razorpay_key_id,
                'razorpay_enabled': settings.razorpay_enabled,
                'stripe_publishable_key': settings.stripe_publishable_key,
                'stripe_enabled': settings.stripe_enabled,
                'gst_percentage': str(settings.gst_percentage),
            }
        })