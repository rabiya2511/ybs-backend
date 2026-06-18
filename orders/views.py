from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Order, OrderDocument
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
    MilestoneUpdateSerializer,
    OrderDocumentSerializer,
)
from services.models import Package
from authentication.permissions import IsAdminOrSuperAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

# Default milestones per service
DEFAULT_MILESTONES = [
    {"name": "Order Confirmed", "status": "completed"},
    {"name": "Documents Collected", "status": "pending"},
    {"name": "Work In Progress", "status": "pending"},
    {"name": "Review & Approval", "status": "pending"},
    {"name": "Completed & Delivered", "status": "pending"},
]

# ══════════════════════════════════════════════
# POST /api/orders/create/
# ══════════════════════════════════════════════
class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        package = get_object_or_404(Package, pk=request.data.get('package'))
        from decimal import Decimal
        base_amount = package.price
        gst_amount = round(base_amount * Decimal('0.18'), 2)
        total_paid = base_amount + gst_amount

        order = Order.objects.create(
            client=request.user,
            service=package.service,
            package=package,
            base_amount=base_amount,
            gst_amount=gst_amount,
            total_paid=total_paid,
            milestones=DEFAULT_MILESTONES,
            **{k: v for k, v in serializer.validated_data.items()
               if k not in ['service', 'package']}
        )

        # Send notification to client
        try:
            from notifications.views import create_notification
            create_notification(
                user=request.user,
                title=f'Order {order.order_number} Created!',
                body=f'Your order for {order.service.name} has been created successfully. Please complete payment to activate.',
                notification_type='ORDER_UPDATE',
                related_order_id=order.id
            )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': f'Order {order.order_number} created successfully!',
            'data': OrderSerializer(order).data
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/orders/my-orders/
# ══════════════════════════════════════════════
class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(client=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response({
            'success': True,
            'count': orders.count(),
            'data': serializer.data
        })


# ══════════════════════════════════════════════
# GET /api/orders/my-orders/<id>/
# ══════════════════════════════════════════════
class MyOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, client=request.user)
        serializer = OrderSerializer(order)
        return Response({
            'success': True,
            'data': serializer.data
        })


# ══════════════════════════════════════════════
# GET /api/orders/admin/
# ══════════════════════════════════════════════
class AdminOrderListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        orders = Order.objects.all()

        status_filter = request.query_params.get('status')
        service_filter = request.query_params.get('service')
        provider_filter = request.query_params.get('provider')

        if status_filter:
            orders = orders.filter(status=status_filter)
        if service_filter:
            orders = orders.filter(service__name__icontains=service_filter)
        if provider_filter:
            orders = orders.filter(provider__id=provider_filter)

        serializer = OrderSerializer(orders, many=True)
        return Response({
            'success': True,
            'count': orders.count(),
            'data': serializer.data
        })


# ══════════════════════════════════════════════
# GET /api/orders/admin/<id>/
# ══════════════════════════════════════════════
class AdminOrderDetailView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(order)
        return Response({
            'success': True,
            'data': serializer.data
        })


# ══════════════════════════════════════════════
# PATCH /api/orders/admin/<id>/status/
# ══════════════════════════════════════════════
class AdminOrderStatusView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderStatusUpdateSerializer(
            order, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()

            # Send notification to client
            try:
                from notifications.views import create_notification
                create_notification(
                    user=order.client,
                    title=f'Order {order.order_number} Updated',
                    body=f'Your order status has been updated to {order.status}.',
                    notification_type='ORDER_UPDATE',
                    related_order_id=order.id
                )
            except Exception as e:
                print(f"Notification error: {e}")

            return Response({
                'success': True,
                'message': f'Order {order.order_number} status updated.',
                'data': OrderSerializer(order).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════
# PATCH /api/orders/admin/<id>/milestone/
# ══════════════════════════════════════════════
class AdminMilestoneUpdateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = MilestoneUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        index = serializer.validated_data['index']
        new_status = serializer.validated_data['status']
        milestones = order.milestones

        if index < 0 or index >= len(milestones):
            return Response({
                'success': False,
                'message': 'Invalid milestone index.'
            }, status=status.HTTP_400_BAD_REQUEST)

        milestones[index]['status'] = new_status
        if new_status == 'completed':
            milestones[index]['completed_at'] = timezone.now().isoformat()

        order.milestones = milestones
        order.save()

        # Send notification to client
        try:
            from notifications.views import create_notification
            create_notification(
                user=order.client,
                title=f'Milestone Completed!',
                body=f'Milestone "{milestones[index]["name"]}" for order {order.order_number} has been completed.',
                notification_type='MILESTONE',
                related_order_id=order.id
            )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': 'Milestone updated successfully.',
            'data': OrderSerializer(order).data
        })


# ══════════════════════════════════════════════
# PATCH /api/orders/admin/<id>/assign-provider/
# ══════════════════════════════════════════════
class AdminAssignProviderView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        provider_id = request.data.get('provider_id')

        if not provider_id:
            return Response({
                'success': False,
                'message': 'provider_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        from authentication.models import User
        provider = get_object_or_404(User, pk=provider_id)

        order.provider = provider
        order.status = 'Active'
        order.save()

        # Send notification to client
        try:
            from notifications.views import create_notification
            create_notification(
                user=order.client,
                title='Provider Assigned!',
                body=f'A provider has been assigned to your order {order.order_number}. Work will begin shortly.',
                notification_type='ORDER_UPDATE',
                related_order_id=order.id
            )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': f'Provider {provider.name} assigned to order {order.order_number}.',
            'data': OrderSerializer(order).data
        })


# ══════════════════════════════════════════════
# POST /api/orders/admin/<id>/documents/
# ══════════════════════════════════════════════
class AdminDocumentUploadView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        file = request.FILES.get('file')
        name = request.data.get('name', file.name if file else 'Document')
        is_deliverable = request.data.get('is_deliverable', True)

        if not file:
            return Response({
                'success': False,
                'message': 'No file provided.'
            }, status=status.HTTP_400_BAD_REQUEST)

        doc = OrderDocument.objects.create(
            order=order,
            name=name,
            file=file,
            uploaded_by=request.user,
            is_deliverable=is_deliverable
        )

        # Send notification to client
        try:
            from notifications.views import create_notification
            create_notification(
                user=order.client,
                title='Document Uploaded!',
                body=f'A new document "{name}" has been uploaded for your order {order.order_number}.',
                notification_type='DOCUMENT',
                related_order_id=order.id
            )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': 'Document uploaded successfully.',
            'data': OrderDocumentSerializer(doc).data
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/orders/admin/stats/
# ══════════════════════════════════════════════
class AdminOrderStatsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        from django.db.models import Sum

        total_revenue = Order.objects.filter(
            status='Done'
        ).aggregate(total=Sum('total_paid'))['total'] or 0

        active_orders = Order.objects.filter(status='Active').count()
        queued_orders = Order.objects.filter(status='Queued').count()
        total_orders = Order.objects.count()

        return Response({
            'success': True,
            'data': {
                'total_revenue': total_revenue,
                'active_orders': active_orders,
                'queued_orders': queued_orders,
                'total_orders': total_orders,
            }
        })