from django.urls import path
from .views import (
    GeneralSettingsView,
    BrandingSettingsView,
    EmailSettingsView,
    PaymentSettingsView,
)

urlpatterns = [
    path('general/', GeneralSettingsView.as_view()),
    path('branding/', BrandingSettingsView.as_view()),
    path('email/', EmailSettingsView.as_view()),
    path('payment/', PaymentSettingsView.as_view()),
]