from django.urls import path
from .views import (
    ClientDashboardView,
    ProviderDashboardView,
    AdminDashboardView,
    FinanceDashboardView,
)

urlpatterns = [
    path('client/', ClientDashboardView.as_view(), name='dashboard-client'),
    path('provider/', ProviderDashboardView.as_view(), name='dashboard-provider'),
    path('admin/', AdminDashboardView.as_view(), name='dashboard-admin'),
    path('finance/', FinanceDashboardView.as_view(), name='dashboard-finance'),
]