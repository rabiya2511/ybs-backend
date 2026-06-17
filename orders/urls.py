from django.urls import path
from .views import (
    OrderCreateView,
    MyOrdersView,
    MyOrderDetailView,
    AdminOrderListView,
    AdminOrderDetailView,
    AdminOrderStatusView,
    AdminMilestoneUpdateView,
    AdminAssignProviderView,
    AdminDocumentUploadView,
    AdminOrderStatsView,
)

urlpatterns = [
    # ── Client Routes ─────────────────────────────
    # Client creates a new order after payment
    path('create/', OrderCreateView.as_view(), name='order-create'),
    # Client sees all their own orders
    path('my-orders/', MyOrdersView.as_view(), name='my-orders'),
    # Client sees one specific order detail
    path('my-orders/<uuid:pk>/', MyOrderDetailView.as_view(), name='my-order-detail'),

    # ── Admin Routes ──────────────────────────────
    # Admin sees all orders with filters
    path('admin/', AdminOrderListView.as_view(), name='admin-orders'),
    # Admin sees dashboard stats
    path('admin/stats/', AdminOrderStatsView.as_view(), name='admin-order-stats'),
    # Admin sees one specific order
    path('admin/<uuid:pk>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
    # Admin updates order status
    path('admin/<uuid:pk>/status/', AdminOrderStatusView.as_view(), name='admin-order-status'),
    # Admin updates a milestone inside an order
    path('admin/<uuid:pk>/milestone/', AdminMilestoneUpdateView.as_view(), name='admin-milestone'),
    # Admin assigns a provider to an order
    path('admin/<uuid:pk>/assign-provider/', AdminAssignProviderView.as_view(), name='admin-assign-provider'),
    # Admin uploads documents or deliverables for client
    path('admin/<uuid:pk>/documents/', AdminDocumentUploadView.as_view(), name='admin-upload-doc'),
]