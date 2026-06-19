from django.urls import path
from .views import (
    ProviderListView,
    ProviderCreateView,
    ProviderDetailView,
    ProviderUpdateView,
    ProviderActivateView,
    ProviderDeactivateView,
    ProviderAvailabilityView,
    ProviderEarningsView,
    ProviderTasksView,
)

urlpatterns = [
    path('', ProviderListView.as_view(), name='provider-list'),
    path('create/', ProviderCreateView.as_view(), name='provider-create'),
    path('<uuid:pk>/', ProviderDetailView.as_view(), name='provider-detail'),
    path('<uuid:pk>/update/', ProviderUpdateView.as_view(), name='provider-update'),
    path('<uuid:pk>/activate/', ProviderActivateView.as_view(), name='provider-activate'),
    path('<uuid:pk>/deactivate/', ProviderDeactivateView.as_view(), name='provider-deactivate'),
    path('<uuid:pk>/availability/', ProviderAvailabilityView.as_view(), name='provider-availability'),
    path('<uuid:pk>/earnings/', ProviderEarningsView.as_view(), name='provider-earnings'),
    path('<uuid:pk>/tasks/', ProviderTasksView.as_view(), name='provider-tasks'),
]