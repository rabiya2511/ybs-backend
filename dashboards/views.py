"""
Dashboard API views.

Queries orders, tasks, invoices, expenses (field names inferred from your
spec doc + mockups since those models.py weren't shared). Confirmed-real
imports: providers, projects, bills, authentication.

NOTE: Task-related fields/enums were patched to match the REAL Task model
(single `status` field, no separate accept/payout tracking). payout_amount /
progress / estimated_hours / payout_status do not exist on Task yet —
stubbed as 0/None until those fields are added.

NOTE: Order.total_amount does not exist on the real Order model — replaced
with Order.total_paid throughout. OrderStatus.IN_PROGRESS/.PENDING_ACCEPT
do not exist — replaced with the real values ACTIVE/REVIEW/DONE/etc.
"""
from datetime import timedelta

from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .permissions import IsClientUser, IsProviderUser, IsAdminPanelUser, IsFinanceUser
from .serializers import (
    ClientDashboardSerializer,
    ProviderDashboardSerializer,
    AdminDashboardSerializer,
    FinanceDashboardSerializer,
)

from orders.models import Order, OrderStatus
from tasks.models import Task, TaskStatus
from providers.models import Provider
from projects.models import Project, Milestone, ProjectStatus
from accounting.models import Invoice, InvoiceStatus, Bill, Expense
from authentication.models import User

ZERO = DecimalField(max_digits=14, decimal_places=2)


def money(value):
    return value or 0


# ---------------------------------------------------------------------------
# CLIENT DASHBOARD
# ---------------------------------------------------------------------------

class ClientDashboardView(APIView):
    """GET /api/dashboard/client"""
    permission_classes = [IsAuthenticated, IsClientUser]

    def get(self, request):
        client = request.user

        projects_qs = Project.objects.filter(client=client)
        active_projects_qs = projects_qs.exclude(
            status__in=[ProjectStatus.DONE, ProjectStatus.CANCELLED]
        )

        total_invested = Order.objects.filter(client=client).aggregate(
            total=Coalesce(Sum('total_paid'), 0, output_field=ZERO)
        )['total']

        total_project_count = projects_qs.count()
        done_project_count = projects_qs.filter(status=ProjectStatus.DONE).count()
        completion_rate = (
            round((done_project_count / total_project_count) * 100, 1)
            if total_project_count else 0
        )

        # Referral rewards: adjust once the referrals app/model is confirmed.
        referral_rewards = 0
        try:
            from referrals.models import ReferralReward  # type: ignore
            referral_rewards = ReferralReward.objects.filter(
                referrer=client, status='Paid'
            ).aggregate(total=Coalesce(Sum('amount'), 0, output_field=ZERO))['total']
        except Exception:
            pass

        stats = {
            'active_projects': active_projects_qs.count(),
            'total_invested': money(total_invested),
            'completion_rate': completion_rate,
            'referral_rewards': money(referral_rewards),
        }

        active_projects = [
            {
                'id': p.id,
                'title': p.title,
                'status': p.status,
                'progress': p.progress,
                'expected_completion_date': p.expected_completion_date,
            }
            for p in active_projects_qs.order_by('-created_at')[:10]
        ]

        recent_orders = [
            {
                'id': o.id,
                'order_number': o.order_number,
                'client_name': client.name,
                'service_name': o.service.name,
                'amount': o.total_paid,
                'status': o.status,
                'created_at': o.created_at,
            }
            for o in Order.objects.filter(client=client).select_related('service').order_by('-created_at')[:5]
        ]

        upcoming_deadlines = [
            {
                'project_title': m.project.title,
                'milestone_title': m.title,
                'due_date': m.due_date,
            }
            for m in Milestone.objects.filter(
                project__client=client, status__in=['pending', 'active'], due_date__isnull=False
            ).select_related('project').order_by('due_date')[:5]
        ]

        data = {
            'stats': stats,
            'active_projects': active_projects,
            'recent_orders': recent_orders,
            'upcoming_deadlines': upcoming_deadlines,
        }
        return Response(ClientDashboardSerializer(data).data)


# ---------------------------------------------------------------------------
# PROVIDER DASHBOARD
# ---------------------------------------------------------------------------

class ProviderDashboardView(APIView):
    """GET /api/dashboard/provider"""
    permission_classes = [IsAuthenticated, IsProviderUser]

    def get(self, request):
        provider = request.user.provider_profile
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        tasks_qs = Task.objects.filter(assigned_to=provider)

        tasks_inbox = tasks_qs.filter(status=TaskStatus.ASSIGNED).count()
        active_tasks_qs = tasks_qs.filter(
            status__in=[TaskStatus.ACCEPTED, TaskStatus.IN_PROGRESS],
        )
        completed_this_month = tasks_qs.filter(
            status=TaskStatus.COMPLETED, updated_at__gte=month_start
        ).count()
        earnings_this_month = 0  # payout_amount field not on Task model yet

        stats = {
            'tasks_inbox': tasks_inbox,
            'active_tasks': active_tasks_qs.count(),
            'completed_this_month': completed_this_month,
            'earnings_this_month': money(earnings_this_month),
        }

        pending_action_tasks = [
            {
                'id': t.id,
                'task_ref': t.task_number,
                'title': t.title,
                'due_date': t.due_date,
                'estimated_hours': None,
                'payout_amount': None,
            }
            for t in tasks_qs.filter(status=TaskStatus.ASSIGNED).order_by('due_date')[:10]
        ]

        active_tasks = [
            {
                'id': t.id,
                'task_ref': t.task_number,
                'service_client': f"{t.order.service.name} ({t.order.client.name})",
                'progress': None,
                'due_date': t.due_date,
                'status': t.status,
            }
            for t in active_tasks_qs.select_related('order', 'order__service', 'order__client').order_by('due_date')[:10]
        ]

        total_earned = 0
        pending_payout = 0
        tasks_total = tasks_qs.filter(status=TaskStatus.COMPLETED).count()

        decided = tasks_qs.exclude(status=TaskStatus.ASSIGNED).count()
        accepted = tasks_qs.filter(
            status__in=[TaskStatus.ACCEPTED, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]
        ).count()
        accept_rate = round((accepted / decided) * 100, 1) if decided else 0

        earnings_summary = {
            'total_earned': money(total_earned),
            'pending_payout': money(pending_payout),
            'tasks_total': tasks_total,
            'accept_rate': accept_rate,
        }

        upcoming = []
        for t in active_tasks_qs.exclude(due_date__isnull=True).order_by('due_date')[:5]:
            days_remaining = (t.due_date - now.date()).days if t.due_date else None
            upcoming.append({
                'task_ref': t.task_number,
                'title': t.title,
                'due_date': t.due_date,
                'days_remaining': days_remaining,
            })

        data = {
            'stats': stats,
            'pending_action_tasks': pending_action_tasks,
            'active_tasks': active_tasks,
            'earnings_summary': earnings_summary,
            'upcoming_deadlines': upcoming,
        }
        return Response(ProviderDashboardSerializer(data).data)


# ---------------------------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------------------------

class AdminDashboardView(APIView):
    """GET /api/dashboard/admin"""
    permission_classes = [IsAuthenticated, IsAdminPanelUser]

    def get(self, request):
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        total_revenue = Order.objects.filter(status=OrderStatus.DONE).aggregate(
            total=Coalesce(Sum('total_paid'), 0, output_field=ZERO)
        )['total']

        active_orders_qs = Order.objects.filter(
            status__in=[OrderStatus.ACTIVE, OrderStatus.REVIEW]
        )
        total_clients = User.objects.filter(role='CLIENT').count()

        pending_tasks_qs = Task.objects.exclude(status__in=[TaskStatus.COMPLETED, TaskStatus.OVERDUE])
        unassigned_tasks_qs = Task.objects.filter(assigned_to__isnull=True).exclude(
            status=TaskStatus.COMPLETED
        )
        active_providers = Provider.objects.filter(is_active=True).count()
        rejected_last_7_days = Task.objects.filter(
            status=TaskStatus.REJECTED, rejected_at__gte=week_ago
        ).count()

        stats = {
            'total_revenue': money(total_revenue),
            'active_orders': active_orders_qs.count(),
            'total_clients': total_clients,
            'pending_tasks': pending_tasks_qs.count(),
            'unassigned_tasks': unassigned_tasks_qs.count(),
            'active_providers': active_providers,
            'rejected_tasks_last_7_days': rejected_last_7_days,
        }

        recent_orders = [
            {
                'id': o.id,
                'order_number': o.order_number,
                'client_name': o.client.name,
                'service_name': o.service.name,
                'amount': o.total_paid,
                'status': o.status,
                'created_at': o.created_at,
            }
            for o in Order.objects.select_related('client', 'service').order_by('-created_at')[:10]
        ]

        unassigned_tasks = [
            {
                'id': t.id,
                'task_ref': t.task_number,
                'title': t.title,
                'client_name': t.order.client.name,
                'category': getattr(t.order.service, 'category', None),
            }
            for t in unassigned_tasks_qs.select_related('order', 'order__client', 'order__service')[:10]
        ]

        revenue_rows = (
            Order.objects.filter(status=OrderStatus.DONE)
            .values('service__name')
            .annotate(revenue=Sum('total_paid'))
            .order_by('-revenue')[:6]
        )
        max_revenue = max((r['revenue'] for r in revenue_rows), default=0) or 1
        revenue_by_service = [
            {
                'service_name': r['service__name'],
                'revenue': r['revenue'],
                'percentage': round(float(r['revenue']) / float(max_revenue) * 100, 1),
            }
            for r in revenue_rows
        ]

        provider_availability = [
            {
                'provider_id': p.id,
                'name': p.user.name,
                'role': p.role,
                'availability_status': p.availability_status,
            }
            for p in Provider.objects.filter(is_active=True).select_related('user')[:10]
        ]

        data = {
            'stats': stats,
            'recent_orders': recent_orders,
            'unassigned_tasks': unassigned_tasks,
            'revenue_by_service': revenue_by_service,
            'provider_availability': provider_availability,
        }
        return Response(AdminDashboardSerializer(data).data)


# ---------------------------------------------------------------------------
# FINANCE DASHBOARD
# ---------------------------------------------------------------------------

class FinanceDashboardView(APIView):
    """GET /api/dashboard/finance"""
    permission_classes = [IsAuthenticated, IsFinanceUser]

    def get(self, request):
        total_revenue = Invoice.objects.filter(status=InvoiceStatus.PAID).aggregate(
            total=Coalesce(Sum('total'), 0, output_field=ZERO)
        )['total']

        outstanding_qs = Invoice.objects.filter(
            status__in=[InvoiceStatus.SENT, InvoiceStatus.DUE, InvoiceStatus.OVERDUE]
        )
        outstanding_total = outstanding_qs.aggregate(
            total=Coalesce(Sum('total'), 0, output_field=ZERO)
        )['total']

        total_expenses_from_expenses = Expense.objects.aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=ZERO)
        )['total']
        total_expenses_from_bills = Bill.objects.filter(status='Paid').aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=ZERO)
        )['total']
        total_expenses = money(total_expenses_from_expenses) + money(total_expenses_from_bills)

        net_profit = money(total_revenue) - total_expenses
        net_margin = round((float(net_profit) / float(total_revenue)) * 100, 1) if total_revenue else 0

        stats = {
            'total_revenue': money(total_revenue),
            'outstanding': money(outstanding_total),
            'outstanding_invoice_count': outstanding_qs.count(),
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'net_margin_percent': net_margin,
        }

        recent_invoices = [
            {
                'id': i.id,
                'invoice_number': i.invoice_number,
                'client_name': i.client.name,
                'amount': i.total,
                'due_date': i.due_date,
                'status': i.status,
            }
            for i in Invoice.objects.select_related('client').order_by('-created_at')[:5]
        ]

        recent_bills = [
            {
                'id': b.id,
                'bill_number': b.bill_number,
                'vendor_name': b.vendor_name,
                'amount': b.amount,
                'due_date': b.due_date,
                'status': b.status,
            }
            for b in Bill.objects.order_by('-created_at')[:5]
        ]

        inflow = money(total_revenue)
        outflow = total_expenses
        cash_flow = {
            'inflow': inflow,
            'outflow': outflow,
            'net_balance': inflow - outflow,
            'receivable': money(outstanding_total),
            'payable': money(
                Bill.objects.filter(status__in=['Pending', 'Overdue']).aggregate(
                    total=Coalesce(Sum('amount'), 0, output_field=ZERO)
                )['total']
            ),
        }

        # Tax summary: Bill model has no gst_amount field, so gst_paid is
        # stubbed at 0 until that's added (or sourced from Expense.gst_amount
        # for vendor-bill-equivalent GST paid, if that's the intended source).
        gst_collected = Invoice.objects.filter(status=InvoiceStatus.PAID).aggregate(
            total=Coalesce(Sum('gst_amount'), 0, output_field=ZERO)
        )['total']
        gst_paid = 0  # Bill model has no gst_amount field
        tds_deducted = 0  # payout_amount/payout_status not on Task model yet

        tax_summary = {
            'gst_collected': money(gst_collected),
            'gst_paid': money(gst_paid),
            'net_gst_liability': money(gst_collected) - money(gst_paid),
            'tds_deducted': money(tds_deducted),
        }

        data = {
            'stats': stats,
            'recent_invoices': recent_invoices,
            'recent_bills': recent_bills,
            'cash_flow': cash_flow,
            'tax_summary': tax_summary,
        }
        return Response(FinanceDashboardSerializer(data).data)