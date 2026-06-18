from django.urls import path
from .views import (
    NotificationListView,
    UnreadCountView,
    MarkReadView,
    MarkAllReadView,
    DeleteNotificationView,
    AdminSendNotificationView,
    ComplianceDeadlineListView,
    CreateDeadlineView,
    CompleteDeadlineView,
)

urlpatterns = [
    # ── Client Routes ─────────────────────────────
    # Get all notifications
    path('', NotificationListView.as_view(), name='notifications'),
    # Get unread count for bell icon
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
    # Mark single notification as read
    path('<uuid:pk>/read/', MarkReadView.as_view(), name='mark-read'),
    # Mark all as read
    path('mark-all-read/', MarkAllReadView.as_view(), name='mark-all-read'),
    # Delete notification
    path('<uuid:pk>/delete/', DeleteNotificationView.as_view(), name='delete-notification'),

    # ── Compliance Deadlines ──────────────────────
    # Client views their deadlines
    path('deadlines/', ComplianceDeadlineListView.as_view(), name='deadlines'),
    # Client marks deadline complete
    path('deadlines/<uuid:pk>/complete/', CompleteDeadlineView.as_view(), name='complete-deadline'),

    # ── Admin Routes ──────────────────────────────
    # Admin sends manual notification
    path('admin/send/', AdminSendNotificationView.as_view(), name='admin-send'),
    # Admin creates compliance deadline
    path('admin/deadlines/create/', CreateDeadlineView.as_view(), name='create-deadline'),
]