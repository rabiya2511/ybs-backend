from django.urls import path
from .views import (
    ServiceListView,
    ServiceDetailView,
    ServiceCreateView,
    ServiceUpdateView,
    PackageCreateView,
    PackageUpdateView,
)

urlpatterns = [
    path('', ServiceListView.as_view(), name='service-list'),
    path('<uuid:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('admin/create/', ServiceCreateView.as_view(), name='service-create'),
    path('admin/<uuid:pk>/update/', ServiceUpdateView.as_view(), name='service-update'),
    path('admin/packages/create/', PackageCreateView.as_view(), name='package-create'),
    path('admin/packages/<uuid:pk>/update/', PackageUpdateView.as_view(), name='package-update'),
]