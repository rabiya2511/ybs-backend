from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Task
from .models import Task, TaskStatus
from .serializers import TaskSerializer, TaskCreateSerializer
from authentication.permissions import IsAdminOrSuperAdmin
from authentication.models import User


# ══════════════════════════════════════════════
# GET /api/tasks/  →  list all tasks
# POST /api/tasks/ →  create task
# ══════════════════════════════════════════════
class TaskListCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        tasks = Task.objects.all()

        # Filters
        status_filter   = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        provider_filter = request.query_params.get('provider')

        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        if provider_filter:
            tasks = tasks.filter(assigned_to__id=provider_filter)

        serializer = TaskSerializer(tasks, many=True)
        return Response({
            'success': True,
            'count': tasks.count(),
            'data': serializer.data
        })

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(created_by=request.user)
            return Response({
                'success': True,
                'message': f'Task {task.task_number} created successfully.',
                'data': TaskSerializer(task).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════
# GET /api/tasks/<id>/    → get single task
# PUT /api/tasks/<id>/    → update task
# DELETE /api/tasks/<id>/ → delete task
# ══════════════════════════════════════════════
class TaskDetailView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        return Response({
            'success': True,
            'data': TaskSerializer(task).data
        })

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': f'Task {task.task_number} updated.',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task_number = task.task_number
        task.delete()
        return Response({
            'success': True,
            'message': f'Task {task_number} deleted.'
        })


# ══════════════════════════════════════════════
# POST /api/tasks/assign/
# ══════════════════════════════════════════════
class TaskAssignView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        task_id     = request.data.get('task_id')
        provider_id = request.data.get('provider_id')

        if not task_id or not provider_id:
            return Response({
                'success': False,
                'message': 'task_id and provider_id are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        task     = get_object_or_404(Task, pk=task_id)
        provider = get_object_or_404(User, pk=provider_id)

        task.assigned_to = provider
        task.status      = TaskStatus.ASSIGNED
        task.save()

        # Notify provider
        try:
            from notifications.views import create_notification
            create_notification(
                user=provider,
                title='New Task Assigned!',
                body=f'Task "{task.title}" has been assigned to you.',
                notification_type='TASK',
                related_order_id=task.order.id if task.order else None
            )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': f'Task assigned to {provider.name}.',
            'data': TaskSerializer(task).data
        })


# ══════════════════════════════════════════════
# POST /api/tasks/reassign/
# ══════════════════════════════════════════════
class TaskReassignView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        task_id     = request.data.get('task_id')
        provider_id = request.data.get('provider_id')
        reason      = request.data.get('reason', '')

        if not task_id or not provider_id:
            return Response({
                'success': False,
                'message': 'task_id and provider_id are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        task         = get_object_or_404(Task, pk=task_id)
        new_provider = get_object_or_404(User, pk=provider_id)
        old_provider = task.assigned_to

        task.assigned_to = new_provider
        task.status      = TaskStatus.ASSIGNED
        task.save()

        # Notify new provider
        try:
            from notifications.views import create_notification
            create_notification(
                user=new_provider,
                title='Task Reassigned to You!',
                body=f'Task "{task.title}" has been reassigned to you.',
                notification_type='TASK',
                related_order_id=task.order.id if task.order else None
            )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': f'Task reassigned from {old_provider.name if old_provider else "Unassigned"} to {new_provider.name}.',
            'data': TaskSerializer(task).data
        })


# ══════════════════════════════════════════════
# POST /api/tasks/complete/
# ══════════════════════════════════════════════
class TaskCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        task_id = request.data.get('task_id')
        notes   = request.data.get('notes', '')

        if not task_id:
            return Response({
                'success': False,
                'message': 'task_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, pk=task_id)

        if task.status == 'Completed':
            return Response({
                'success': False,
                'message': 'Task is already completed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        task.status           = 'Completed'
        task.completed_at     = timezone.now()
        task.completion_notes = notes
        task.save()

        # Notify order client
        try:
            from notifications.views import create_notification
            if task.order:
                create_notification(
                    user=task.order.client,
                    title='Task Completed!',
                    body=f'Task "{task.title}" for your order {task.order.order_number} has been completed.',
                    notification_type='TASK',
                    related_order_id=task.order.id
                )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': f'Task {task.task_number} marked as completed.',
            'data': TaskSerializer(task).data
        })


# ══════════════════════════════════════════════
# POST /api/tasks/reject/
# ══════════════════════════════════════════════
class TaskRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        task_id = request.data.get('task_id')
        reason  = request.data.get('reason', '')

        if not task_id:
            return Response({
                'success': False,
                'message': 'task_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, pk=task_id)

        if task.status == 'Completed':
            return Response({
                'success': False,
                'message': 'Cannot reject a completed task.'
            }, status=status.HTTP_400_BAD_REQUEST)

        task.status           = 'Rejected'
        task.rejected_at      = timezone.now()
        task.rejection_reason = reason
        task.save()

        return Response({
            'success': True,
            'message': f'Task {task.task_number} rejected.',
            'data': TaskSerializer(task).data
        })


# ══════════════════════════════════════════════
# GET /api/tasks/unassigned/
# ══════════════════════════════════════════════
class TaskUnassignedView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        tasks = Task.objects.filter(status='Unassigned').order_by('-created_at')
        serializer = TaskSerializer(tasks, many=True)
        return Response({
            'success': True,
            'count': tasks.count(),
            'data': serializer.data
        })


# ══════════════════════════════════════════════
# GET /api/tasks/overdue/
# ══════════════════════════════════════════════
class TaskOverdueView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        today = timezone.now().date()
        tasks = Task.objects.filter(
            due_date__lt=today
        ).exclude(
            status__in=['Completed', 'Rejected']
        ).order_by('due_date')

        serializer = TaskSerializer(tasks, many=True)
        return Response({
            'success': True,
            'count': tasks.count(),
            'data': serializer.data
        })