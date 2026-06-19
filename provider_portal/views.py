from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count
from providers.models import Provider, ProviderPayout
from orders.models import Order

from rest_framework.parsers import MultiPartParser, FormParser


def get_provider_or_404(user):
    return get_object_or_404(Provider, user=user)


# ══════════════════════════════════════════════
# GET /api/provider-portal/dashboard/
# Provider's own dashboard summary
# ══════════════════════════════════════════════
class ProviderDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        provider = get_provider_or_404(request.user)
        orders = Order.objects.filter(provider=request.user)

        active_count = orders.filter(status='Active').count()
        review_count = orders.filter(status='Review').count()
        done_count = orders.filter(status='Done').count()
        queued_count = orders.filter(status='Queued').count()

        total_earned = ProviderPayout.objects.filter(
            provider=provider, status='Paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

        pending_amount = ProviderPayout.objects.filter(
            provider=provider, status='Pending'
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'success': True,
            'data': {
                'provider_name': provider.user.name,
                'role': provider.role,
                'availability_status': provider.availability_status,
                'avg_rating': provider.avg_rating,
                'total_orders_completed': provider.total_orders_completed,
                'active_tasks': active_count,
                'review_tasks': review_count,
                'done_tasks': done_count,
                'queued_tasks': queued_count,
                'total_earned': str(total_earned),
                'pending_amount': str(pending_amount),
            }
        })


# ══════════════════════════════════════════════
# GET /api/provider-portal/tasks/
# Provider's assigned tasks (own orders)
# ══════════════════════════════════════════════
class MyTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(provider=request.user)

        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)

        data = []
        for o in orders:
            data.append({
                'id': str(o.id),
                'order_number': o.order_number,
                'service_name': o.service.name if o.service else '',
                'client_name': o.client.name,
                'status': o.status,
                'expected_completion_date': o.expected_completion_date,
                'created_at': o.created_at,
            })

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/provider-portal/tasks/<id>/accept/
# Provider accepts a task
# ══════════════════════════════════════════════
class AcceptTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, provider=request.user)

        if order.status != 'Queued':
            return Response({
                'success': False,
                'message': f'Task cannot be accepted from status "{order.status}".'
            }, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'Active'
        order.save()

        return Response({
            'success': True,
            'message': f'Task {order.order_number} accepted.'
        })


# ══════════════════════════════════════════════
# POST /api/provider-portal/tasks/<id>/reject/
# Provider rejects a task (unassigns themselves)
# ══════════════════════════════════════════════
class RejectTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, provider=request.user)
        reason = request.data.get('reason', '')

        order.provider = None
        order.status = 'Queued'
        order.internal_notes = (order.internal_notes or '') + f"\nRejected by provider: {reason}"
        order.save()

        return Response({
            'success': True,
            'message': f'Task {order.order_number} rejected and unassigned.'
        })


# ══════════════════════════════════════════════
# POST /api/provider-portal/tasks/<id>/start/
# Provider starts working on task
# ══════════════════════════════════════════════
class StartTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, provider=request.user)

        if order.status not in ['Queued', 'Active']:
            return Response({
                'success': False,
                'message': f'Task cannot be started from status "{order.status}".'
            }, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'Active'
        order.save()

        return Response({
            'success': True,
            'message': f'Task {order.order_number} started.'
        })


# ══════════════════════════════════════════════
# POST /api/provider-portal/tasks/<id>/complete/
# Provider marks task complete
# ══════════════════════════════════════════════
class CompleteTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, provider=request.user)

        order.status = 'Review'
        order.save()

        provider = get_provider_or_404(request.user)
        provider.total_orders_completed += 1
        provider.save()

        return Response({
            'success': True,
            'message': f'Task {order.order_number} marked complete and sent for review.'
        })


# ══════════════════════════════════════════════
# POST /api/provider-portal/tasks/<id>/upload/
# Provider uploads deliverable file
# ══════════════════════════════════════════════



class UploadTaskFileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # ← MUST have this

    def post(self, request, pk):
        from orders.models import OrderDocument

        print("FILES:", request.FILES)        # ← debug
        print("DATA:", request.data)          # ← debug

        order = get_object_or_404(Order, pk=pk, provider=request.user)
        file = request.FILES.get('file')

        if not file:
            return Response({
                'success': False,
                'message': 'file is required.',
                'files_received': str(request.FILES),
            }, status=status.HTTP_400_BAD_REQUEST)

        document = OrderDocument.objects.create(
            order=order,
            file=file,
            name=file.name,
            uploaded_by=request.user,
        )

        return Response({
            'success': True,
            'message': 'File uploaded successfully.',
            'data': {
                'id': str(document.id),
                'file': document.file.url if document.file else None,
            }
        }, status=status.HTTP_201_CREATED)

# ══════════════════════════════════════════════
# GET /api/provider-portal/earnings/
# Provider's own earnings
# ══════════════════════════════════════════════
class MyEarningsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        provider = get_provider_or_404(request.user)
        payouts = ProviderPayout.objects.filter(provider=provider)

        total_earned = payouts.filter(status='Paid').aggregate(
            total=Sum('amount'))['total'] or 0
        pending_amount = payouts.filter(status='Pending').aggregate(
            total=Sum('amount'))['total'] or 0

        return Response({
            'success': True,
            'data': {
                'total_earned': str(total_earned),
                'pending_amount': str(pending_amount),
                'total_orders_completed': provider.total_orders_completed,
                'commission_type': provider.commission_type,
                'commission_value': str(provider.commission_value),
            }
        })


# ══════════════════════════════════════════════
# GET /api/provider-portal/payments/
# Provider's payment/payout history
# ══════════════════════════════════════════════
class MyPaymentsHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        provider = get_provider_or_404(request.user)
        payouts = ProviderPayout.objects.filter(provider=provider)

        data = []
        for p in payouts:
            data.append({
                'id': str(p.id),
                'order_number': p.order.order_number if p.order else None,
                'amount': str(p.amount),
                'status': p.status,
                'paid_at': p.paid_at,
                'created_at': p.created_at,
            })

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })
    