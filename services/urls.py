from django.urls import path
from .views import (
    ServiceListView,
    ServiceDetailView,
    ServiceCreateView,
    ServiceUpdateView,
    PackageCreateView,
    PackageUpdateView,
)
from .category_views import (
    CategoryListView,
    CategoryCreateView,
    CategoryDetailView,
    CategoryUpdateView,
)

urlpatterns = [
    # ── Service Routes ────────────────────────────
    path('', ServiceListView.as_view(), name='service-list'),
    path('<uuid:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('admin/create/', ServiceCreateView.as_view(), name='service-create'),
    path('admin/<uuid:pk>/update/', ServiceUpdateView.as_view(), name='service-update'),

    # ── Package Routes ────────────────────────────
    path('admin/packages/create/', PackageCreateView.as_view(), name='package-create'),
    path('admin/packages/<uuid:pk>/update/', PackageUpdateView.as_view(), name='package-update'),

    # ── Category Routes ───────────────────────────
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<uuid:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<uuid:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
]