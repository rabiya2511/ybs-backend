from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Project, Milestone, ProjectDocument
from authentication.permissions import IsAdminOrSuperAdmin

# ══════════════════════════════════════════════
# GET /api/projects/
# Client gets their projects
# ══════════════════════════════════════════════
class ProjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.filter(client=request.user)
        data = []
        for p in projects:
            data.append({
                'id': str(p.id),
                'title': p.title,
                'status': p.status,
                'progress': p.progress,
                'order_number': p.order.order_number,
                'service_name': p.order.service.name if p.order.service else '',
                'expected_completion_date': p.expected_completion_date,
                'created_at': p.created_at,
            })
        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/projects/
# Admin creates a project for an order
# ══════════════════════════════════════════════
class ProjectCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        from orders.models import Order
        order_id = request.data.get('order_id')
        title = request.data.get('title')
        description = request.data.get('description', '')
        expected_completion_date = request.data.get('expected_completion_date')

        if not order_id or not title:
            return Response({
                'success': False,
                'message': 'order_id and title are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        import uuid
        try:
            order = Order.objects.get(pk=uuid.UUID(str(order_id)))
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if project already exists for this order
        if hasattr(order, 'project'):
            return Response({
                'success': False,
                'message': 'A project already exists for this order.'
            }, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.create(
            order=order,
            client=order.client,
            assigned_provider=order.provider,
            title=title,
            description=description,
            expected_completion_date=expected_completion_date,
        )

        return Response({
            'success': True,
            'message': f'Project created successfully.',
            'data': {
                'id': str(project.id),
                'title': project.title,
                'status': project.status,
                'order_number': order.order_number,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/projects/<id>/
# Get single project detail
# ══════════════════════════════════════════════
class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if request.user.role in ['STAFF', 'SUPER_ADMIN', 'FINANCE_ADMIN']:
            project = get_object_or_404(Project, pk=pk)
        else:
            project = get_object_or_404(Project, pk=pk, client=request.user)

        milestones = [{
            'id': str(m.id),
            'title': m.title,
            'description': m.description,
            'status': m.status,
            'order': m.order,
            'due_date': m.due_date,
            'completed_at': m.completed_at,
        } for m in project.milestones.all()]

        documents = [{
            'id': str(d.id),
            'name': d.name,
            'file': request.build_absolute_uri(d.file.url) if d.file else None,
            'is_deliverable': d.is_deliverable,
            'created_at': d.created_at,
        } for d in project.documents.all()]

        return Response({
            'success': True,
            'data': {
                'id': str(project.id),
                'title': project.title,
                'description': project.description,
                'status': project.status,
                'progress': project.progress,
                'order_number': project.order.order_number,
                'service_name': project.order.service.name if project.order.service else '',
                'package_name': project.order.package.name if project.order.package else '',
                'client_name': project.client.name,
                'assigned_provider': project.assigned_provider.name if project.assigned_provider else None,
                'start_date': project.start_date,
                'expected_completion_date': project.expected_completion_date,
                'completed_date': project.completed_date,
                'milestones': milestones,
                'documents': documents,
                'created_at': project.created_at,
            }
        })


# ══════════════════════════════════════════════
# PUT /api/projects/<id>/
# Admin updates project
# ══════════════════════════════════════════════
class ProjectUpdateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        project.title = request.data.get('title', project.title)
        project.description = request.data.get('description', project.description)
        project.status = request.data.get('status', project.status)
        project.progress = request.data.get('progress', project.progress)
        project.expected_completion_date = request.data.get('expected_completion_date', project.expected_completion_date)
        project.internal_notes = request.data.get('internal_notes', project.internal_notes)
        project.save()

        return Response({
            'success': True,
            'message': 'Project updated successfully.',
            'data': {
                'id': str(project.id),
                'title': project.title,
                'status': project.status,
                'progress': project.progress,
            }
        })

    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project.delete()
        return Response({
            'success': True,
            'message': 'Project deleted successfully.'
        })


# ══════════════════════════════════════════════
# POST /api/projects/<id>/complete/
# Mark project as complete
# ══════════════════════════════════════════════
class ProjectCompleteView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project.status = 'Done'
        project.progress = 100
        project.completed_date = timezone.now().date()
        project.save()

        # Update order status
        project.order.status = 'Done'
        project.order.save()

        # Notify client
        try:
            from notifications.views import create_notification
            create_notification(
                user=project.client,
                title='Project Completed!',
                body=f'Your project "{project.title}" has been completed and delivered.',
                notification_type='ORDER_UPDATE',
                related_order_id=project.order.id
            )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': f'Project "{project.title}" marked as complete.',
            'data': {
                'id': str(project.id),
                'status': project.status,
                'progress': project.progress,
                'completed_date': project.completed_date,
            }
        })


# ══════════════════════════════════════════════
# GET /api/projects/milestones/
# Get all milestones for client projects
# ══════════════════════════════════════════════
class MilestoneListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get('project_id')
        if project_id:
            milestones = Milestone.objects.filter(project__id=project_id)
        else:
            milestones = Milestone.objects.filter(project__client=request.user)

        data = [{
            'id': str(m.id),
            'project_id': str(m.project.id),
            'project_title': m.project.title,
            'title': m.title,
            'description': m.description,
            'status': m.status,
            'order': m.order,
            'due_date': m.due_date,
            'completed_at': m.completed_at,
        } for m in milestones]

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/projects/milestones/
# Admin creates a milestone
# ══════════════════════════════════════════════
class MilestoneCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        project_id = request.data.get('project_id')
        title = request.data.get('title')
        description = request.data.get('description', '')
        order = request.data.get('order', 0)
        due_date = request.data.get('due_date')

        if not project_id or not title:
            return Response({
                'success': False,
                'message': 'project_id and title are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=project_id)

        milestone = Milestone.objects.create(
            project=project,
            title=title,
            description=description,
            order=order,
            due_date=due_date,
        )

        return Response({
            'success': True,
            'message': 'Milestone created successfully.',
            'data': {
                'id': str(milestone.id),
                'title': milestone.title,
                'status': milestone.status,
                'order': milestone.order,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# PUT /api/projects/milestones/<id>/
# Admin updates a milestone
# ══════════════════════════════════════════════
class MilestoneUpdateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        milestone = get_object_or_404(Milestone, pk=pk)
        old_status = milestone.status

        milestone.title = request.data.get('title', milestone.title)
        milestone.description = request.data.get('description', milestone.description)
        milestone.status = request.data.get('status', milestone.status)
        milestone.order = request.data.get('order', milestone.order)
        milestone.due_date = request.data.get('due_date', milestone.due_date)

        if milestone.status == 'completed' and old_status != 'completed':
            milestone.completed_at = timezone.now()

        milestone.save()

        # Update project progress
        project = milestone.project
        total = project.milestones.count()
        completed = project.milestones.filter(status='completed').count()
        project.progress = int((completed / total) * 100) if total > 0 else 0
        project.save()

        # Notify client
        try:
            from notifications.views import create_notification
            create_notification(
                user=project.client,
                title=f'Milestone Updated: {milestone.title}',
                body=f'Milestone "{milestone.title}" status changed to {milestone.status}.',
                notification_type='MILESTONE',
                related_order_id=project.order.id
            )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': 'Milestone updated successfully.',
            'data': {
                'id': str(milestone.id),
                'title': milestone.title,
                'status': milestone.status,
                'project_progress': project.progress,
            }
        })


# ══════════════════════════════════════════════
# GET /api/projects/<id>/documents/
# Get all documents for a project
# ══════════════════════════════════════════════
class ProjectDocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        documents = project.documents.all()

        data = [{
            'id': str(d.id),
            'name': d.name,
            'file': request.build_absolute_uri(d.file.url) if d.file else None,
            'is_deliverable': d.is_deliverable,
            'uploaded_by': d.uploaded_by.name if d.uploaded_by else None,
            'created_at': d.created_at,
        } for d in documents]

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/projects/<id>/documents/
# Upload document to a project
# ══════════════════════════════════════════════
class ProjectDocumentUploadView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        file = request.FILES.get('file')
        name = request.data.get('name', file.name if file else 'Document')
        is_deliverable = request.data.get('is_deliverable', False)

        if not file:
            return Response({
                'success': False,
                'message': 'No file provided.'
            }, status=status.HTTP_400_BAD_REQUEST)

        doc = ProjectDocument.objects.create(
            project=project,
            uploaded_by=request.user,
            name=name,
            file=file,
            is_deliverable=is_deliverable
        )

        # Notify client if deliverable
        if is_deliverable:
            try:
                from notifications.views import create_notification
                create_notification(
                    user=project.client,
                    title='Deliverable Ready!',
                    body=f'A deliverable "{name}" has been uploaded for your project "{project.title}".',
                    notification_type='DOCUMENT',
                    related_order_id=project.order.id
                )
            except Exception as e:
                print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': 'Document uploaded successfully.',
            'data': {
                'id': str(doc.id),
                'name': doc.name,
                'is_deliverable': doc.is_deliverable,
            }
        }, status=status.HTTP_201_CREATED)