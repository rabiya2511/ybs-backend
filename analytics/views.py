from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from authentication.permissions import IsAdminOrSuperAdmin
from orders.models import Order
from accounting.models import Invoice
from services.models import Service
from providers.models import Provider
from authentication.models import User


# ══════════════════════════════════════════════
# GET /api/analytics/revenue/
# Revenue analytics over time
# ══════════════════════════════════════════════
class RevenueAnalyticsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        monthly = Invoice.objects.filter(
            status='Paid'
        ).annotate(
            month=TruncMonth('paid_at')
        ).values('month').annotate(
            revenue=Sum('total')
        ).order_by('month')[:12]

        data = [{
            'month': m['month'].strftime('%Y-%m') if m['month'] else '',
            'revenue': str(m['revenue']),
        } for m in monthly]

        total_revenue = Invoice.objects.filter(
            status='Paid'
        ).aggregate(total=Sum('total'))['total'] or 0

        return Response({
            'success': True,
            'data': {
                'total_revenue': str(total_revenue),
                'monthly_trend': data,
            }
        })


# ══════════════════════════════════════════════
# GET /api/analytics/orders/
# Order analytics - trends and status breakdown
# ══════════════════════════════════════════════
class OrderAnalyticsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        total_orders = Order.objects.count()

        by_status = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        monthly = Order.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')[:12]

        status_data = [{
            'status': s['status'],
            'count': s['count'],
        } for s in by_status]

        monthly_data = [{
            'month': m['month'].strftime('%Y-%m') if m['month'] else '',
            'count': m['count'],
        } for m in monthly]

        return Response({
            'success': True,
            'data': {
                'total_orders': total_orders,
                'by_status': status_data,
                'monthly_trend': monthly_data,
            }
        })


# ══════════════════════════════════════════════
# GET /api/analytics/services/
# Service performance analytics
# ══════════════════════════════════════════════
class ServiceAnalyticsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        services = Service.objects.annotate(
            order_count=Count('packages__orders')
        ).order_by('-order_count')[:20]

        data = [{
            'id': str(s.id),
            'name': s.name,
            'category': s.category,
            'order_count': s.order_count,
            'starting_price': str(s.starting_price),
        } for s in services]

        by_category = Service.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')

        category_data = [{
            'category': c['category'],
            'service_count': c['count'],
        } for c in by_category]

        return Response({
            'success': True,
            'data': {
                'top_services': data,
                'by_category': category_data,
            }
        })


# ══════════════════════════════════════════════
# GET /api/analytics/providers/
# Provider performance analytics
# ══════════════════════════════════════════════
class ProviderAnalyticsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        total_providers = Provider.objects.count()
        active_providers = Provider.objects.filter(is_active=True).count()

        top_providers = Provider.objects.order_by(
            '-total_orders_completed'
        )[:10]

        data = [{
            'id': str(p.id),
            'name': p.user.name,
            'role': p.role,
            'total_orders_completed': p.total_orders_completed,
            'avg_rating': p.avg_rating,
            'avg_completion_days': p.avg_completion_days,
        } for p in top_providers]

        avg_rating = Provider.objects.aggregate(
            avg=Avg('avg_rating')
        )['avg'] or 0

        return Response({
            'success': True,
            'data': {
                'total_providers': total_providers,
                'active_providers': active_providers,
                'overall_avg_rating': round(avg_rating, 2),
                'top_providers': data,
            }
        })


# ══════════════════════════════════════════════
# GET /api/analytics/clients/
# Client analytics
# ══════════════════════════════════════════════
class ClientAnalyticsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        total_clients = User.objects.filter(role='CLIENT').count()

        top_clients = Order.objects.values(
            'client__name', 'client__email'
        ).annotate(
            order_count=Count('id'),
            total_spent=Sum('total_paid')
        ).order_by('-total_spent')[:10]

        data = [{
            'client_name': c['client__name'],
            'client_email': c['client__email'],
            'order_count': c['order_count'],
            'total_spent': str(c['total_spent']) if c['total_spent'] else '0',
        } for c in top_clients]

        new_clients_monthly = User.objects.filter(
            role='CLIENT'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')[:12]

        new_clients_data = [{
            'month': m['month'].strftime('%Y-%m') if m['month'] else '',
            'count': m['count'],
        } for m in new_clients_monthly]

        return Response({
            'success': True,
            'data': {
                'total_clients': total_clients,
                'top_clients': data,
                'new_clients_monthly': new_clients_data,
            }
        })


# ══════════════════════════════════════════════
# GET /api/analytics/growth/
# Growth metrics over time
# ══════════════════════════════════════════════
class GrowthAnalyticsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        orders_monthly = Order.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')[:12]

        revenue_monthly = Invoice.objects.filter(
            status='Paid'
        ).annotate(
            month=TruncMonth('paid_at')
        ).values('month').annotate(
            revenue=Sum('total')
        ).order_by('month')[:12]

        users_monthly = User.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')[:12]

        return Response({
            'success': True,
            'data': {
                'orders_growth': [{
                    'month': m['month'].strftime('%Y-%m') if m['month'] else '',
                    'count': m['count'],
                } for m in orders_monthly],
                'revenue_growth': [{
                    'month': m['month'].strftime('%Y-%m') if m['month'] else '',
                    'revenue': str(m['revenue']),
                } for m in revenue_monthly],
                'user_growth': [{
                    'month': m['month'].strftime('%Y-%m') if m['month'] else '',
                    'count': m['count'],
                } for m in users_monthly],
            }
        })


# ══════════════════════════════════════════════
# GET /api/analytics/compliance/
# Compliance/deadline analytics
# ══════════════════════════════════════════════
class ComplianceAnalyticsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        from notifications.models import ComplianceDeadline
        from django.utils import timezone

        total_deadlines = ComplianceDeadline.objects.count()
        upcoming = ComplianceDeadline.objects.filter(
            due_date__gte=timezone.now().date(),
            is_completed=False
        ).count()
        overdue = ComplianceDeadline.objects.filter(
            due_date__lt=timezone.now().date(),
            is_completed=False
        ).count()
        completed = ComplianceDeadline.objects.filter(
            is_completed=True
        ).count()

        return Response({
            'success': True,
            'data': {
                'total_deadlines': total_deadlines,
                'upcoming': upcoming,
                'overdue': overdue,
                'completed': completed,
            }
        })