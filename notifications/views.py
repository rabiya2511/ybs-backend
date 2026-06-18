from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Notification, ComplianceDeadline
from authentication.permissions import IsAdminOrSuperAdmin
import uuid

# ══════════════════════════════════════════════
# Helper function to create notifications
# Used by other modules (orders, payments, etc)
# ══════════════════════════════════════════════
def create_notification(user, title, body, notification_type='GENERAL',
                        related_order_id=None, related_invoice_id=None):
    Notification.objects.create(
        user=user,
        title=title,
        body=body,
        notification_type=notification_type,
        related_order_id=related_order_id,
        related_invoice_id=related_invoice_id,
    )

# ══════════════════════════════════════════════
# GET /api/notifications/
# Client gets their notifications
# ══════════════════════════════════════════════
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)

        # Filter by read/unread
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            notifications = notifications.filter(is_read=is_read.lower() == 'true')

        data = []
        for n in notifications:
            data.append({
                'id': str(n.id),
                'title': n.title,
                'body': n.body,
                'type': n.notification_type,
                'is_read': n.is_read,
                'read_at': n.read_at,
                'related_order_id': str(n.related_order_id) if n.related_order_id else None,
                'created_at': n.created_at,
            })

        unread_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()

        return Response({
            'success': True,
            'unread_count': unread_count,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# GET /api/notifications/unread-count/
# Returns just the unread count for bell icon
# ══════════════════════════════════════════════
class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return Response({
            'success': True,
            'unread_count': count
        })


# ══════════════════════════════════════════════
# PATCH /api/notifications/<id>/read/
# Mark single notification as read
# ══════════════════════════════════════════════
class MarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        notification = get_object_or_404(
            Notification, pk=pk, user=request.user
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        return Response({
            'success': True,
            'message': 'Notification marked as read.'
        })


# ══════════════════════════════════════════════
# PATCH /api/notifications/mark-all-read/
# Mark all notifications as read
# ══════════════════════════════════════════════
class MarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response({
            'success': True,
            'message': 'All notifications marked as read.'
        })


# ══════════════════════════════════════════════
# DELETE /api/notifications/<id>/
# Delete a notification
# ══════════════════════════════════════════════
class DeleteNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        notification = get_object_or_404(
            Notification, pk=pk, user=request.user
        )
        notification.delete()
        return Response({
            'success': True,
            'message': 'Notification deleted.'
        })


# ══════════════════════════════════════════════
# Admin — Send manual notification to a client
# POST /api/notifications/admin/send/
# ══════════════════════════════════════════════
class AdminSendNotificationView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        from authentication.models import User
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        body = request.data.get('body')
        notification_type = request.data.get('type', 'GENERAL')

        if not user_id or not title or not body:
            return Response({
                'success': False,
                'message': 'user_id, title and body are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, pk=user_id)
        create_notification(user, title, body, notification_type)

        return Response({
            'success': True,
            'message': f'Notification sent to {user.email}.'
        })


# ══════════════════════════════════════════════
# GET /api/notifications/deadlines/
# Client views their compliance deadlines
# ══════════════════════════════════════════════
class ComplianceDeadlineListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        deadlines = ComplianceDeadline.objects.filter(
            user=request.user,
            is_completed=False
        )

        data = []
        for d in deadlines:
            days_remaining = (d.due_date - timezone.now().date()).days
            data.append({
                'id': str(d.id),
                'title': d.title,
                'description': d.description,
                'company_name': d.company_name,
                'category': d.category,
                'due_date': d.due_date,
                'days_remaining': days_remaining,
                'is_completed': d.is_completed,
            })

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/notifications/deadlines/create/
# Admin creates a compliance deadline for client
# ══════════════════════════════════════════════
class CreateDeadlineView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        from authentication.models import User
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        due_date = request.data.get('due_date')
        category = request.data.get('category', 'OTHER')
        company_name = request.data.get('company_name', '')
        description = request.data.get('description', '')

        if not user_id or not title or not due_date:
            return Response({
                'success': False,
                'message': 'user_id, title and due_date are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, pk=user_id)

        deadline = ComplianceDeadline.objects.create(
            user=user,
            title=title,
            description=description,
            company_name=company_name,
            due_date=due_date,
            category=category,
        )

        # Send notification to client
        create_notification(
            user=user,
            title=f'New Compliance Deadline: {title}',
            body=f'You have a {category} deadline due on {due_date}. Company: {company_name}',
            notification_type='COMPLIANCE'
        )

        return Response({
            'success': True,
            'message': 'Deadline created successfully.',
            'data': {
                'id': str(deadline.id),
                'title': deadline.title,
                'due_date': deadline.due_date,
                'category': deadline.category,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# PATCH /api/notifications/deadlines/<id>/complete/
# Mark deadline as completed
# ══════════════════════════════════════════════
class CompleteDeadlineView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        deadline = get_object_or_404(
            ComplianceDeadline, pk=pk, user=request.user
        )
        deadline.is_completed = True
        deadline.save()

        return Response({
            'success': True,
            'message': f'Deadline "{deadline.title}" marked as completed.'
        })
# ══════════════════════════════════════════════
# GET /api/notifications/unread/
# Client views only unread notifications
# ══════════════════════════════════════════════
class UnreadNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )
        data = []
        for n in notifications:
            data.append({
                'id': str(n.id),
                'title': n.title,
                'message': n.message,
                'notification_type': n.notification_type,
                'is_read': n.is_read,
                'created_at': n.created_at,
            })
        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })