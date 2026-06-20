from django.urls import path
from .views import (
    RevenueAnalyticsView,
    OrderAnalyticsView,
    ServiceAnalyticsView,
    ProviderAnalyticsView,
    ClientAnalyticsView,
    GrowthAnalyticsView,
    ComplianceAnalyticsView,
)

urlpatterns = [
    path('revenue/', RevenueAnalyticsView.as_view()),
    path('orders/', OrderAnalyticsView.as_view()),
    path('services/', ServiceAnalyticsView.as_view()),
    path('providers/', ProviderAnalyticsView.as_view()),
    path('clients/', ClientAnalyticsView.as_view()),
    path('growth/', GrowthAnalyticsView.as_view()),
    path('compliance/', ComplianceAnalyticsView.as_view()),
]
