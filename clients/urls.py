from django.urls import path
from .views import (
    ClientListView,
    ClientCreateView,
    ClientDetailView,
    ClientUpdateView,
    ClientSuspendView,
    ClientActivateView,
    ClientOrdersView,
    ClientProjectsView,
    ClientInvoicesView,
)

urlpatterns = [
    # List all clients / Create new client
    path('', ClientListView.as_view(), name='client-list'),
    path('create/', ClientCreateView.as_view(), name='client-create'),

    # Single client detail / update / delete
    path('<uuid:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('<uuid:pk>/update/', ClientUpdateView.as_view(), name='client-update'),

    # Suspend / Activate
    path('<uuid:pk>/suspend/', ClientSuspendView.as_view(), name='client-suspend'),
    path('<uuid:pk>/activate/', ClientActivateView.as_view(), name='client-activate'),

    # Related data
    path('<uuid:pk>/orders/', ClientOrdersView.as_view(), name='client-orders'),
    path('<uuid:pk>/projects/', ClientProjectsView.as_view(), name='client-projects'),
    path('<uuid:pk>/invoices/', ClientInvoicesView.as_view(), name='client-invoices'),
]