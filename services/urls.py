from django.urls import path
from .views import (
    ServiceListView,
    ServiceDetailView,
    ServiceCreateView,
    ServiceUpdateView,
    PackageCreateView,
    PackageUpdateView,
    ServiceDeleteView,
    PackageDeleteView,
    FeaturedServicesView,
    PopularServicesView,
    ServicesByCategoryView,
    ServicePackagesView,
)

urlpatterns = [
    # ── Public Routes ─────────────────────────────
    path('', ServiceListView.as_view(), name='service-list'),
    path('featured/', FeaturedServicesView.as_view(), name='featured-services'),
    path('popular/', PopularServicesView.as_view(), name='popular-services'),
    path('category/<str:category>/', ServicesByCategoryView.as_view(), name='services-by-category'),
    path('<uuid:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('<uuid:pk>/packages/', ServicePackagesView.as_view(), name='service-packages'),

    # ── Admin Routes ──────────────────────────────
    path('admin/create/', ServiceCreateView.as_view(), name='service-create'),
    path('admin/<uuid:pk>/update/', ServiceUpdateView.as_view(), name='service-update'),
    path('admin/<uuid:pk>/delete/', ServiceDeleteView.as_view(), name='service-delete'),
    path('admin/packages/create/', PackageCreateView.as_view(), name='package-create'),
    path('admin/packages/<uuid:pk>/update/', PackageUpdateView.as_view(), name='package-update'),
    path('admin/packages/<uuid:pk>/delete/', PackageDeleteView.as_view(), name='package-delete'),
]