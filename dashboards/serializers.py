from rest_framework import serializers


# ---------------------------------------------------------------------------
# Shared small serializers (table rows used across dashboards)
# ---------------------------------------------------------------------------

class RecentOrderRowSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    order_number = serializers.CharField()
    client_name = serializers.CharField()
    service_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class UnassignedTaskRowSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    task_ref = serializers.CharField()
    title = serializers.CharField()
    client_name = serializers.CharField()
    category = serializers.CharField(allow_null=True)


class RevenueByServiceRowSerializer(serializers.Serializer):
    service_name = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    percentage = serializers.FloatField()


class ProviderAvailabilityRowSerializer(serializers.Serializer):
    provider_id = serializers.UUIDField()
    name = serializers.CharField()
    role = serializers.CharField()
    availability_status = serializers.CharField()


# ---------------------------------------------------------------------------
# CLIENT DASHBOARD  (GET /api/dashboard/client)
# ---------------------------------------------------------------------------

class ClientStatsSerializer(serializers.Serializer):
    active_projects = serializers.IntegerField()
    total_invested = serializers.DecimalField(max_digits=14, decimal_places=2)
    completion_rate = serializers.FloatField()
    referral_rewards = serializers.DecimalField(max_digits=12, decimal_places=2)


class ClientActiveProjectRowSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    status = serializers.CharField()
    progress = serializers.IntegerField()
    expected_completion_date = serializers.DateField(allow_null=True)


class ClientDeadlineRowSerializer(serializers.Serializer):
    project_title = serializers.CharField()
    milestone_title = serializers.CharField()
    due_date = serializers.DateField(allow_null=True)


class ClientDashboardSerializer(serializers.Serializer):
    stats = ClientStatsSerializer()
    active_projects = ClientActiveProjectRowSerializer(many=True)
    recent_orders = RecentOrderRowSerializer(many=True)
    upcoming_deadlines = ClientDeadlineRowSerializer(many=True)


# ---------------------------------------------------------------------------
# PROVIDER DASHBOARD  (GET /api/dashboard/provider)
# ---------------------------------------------------------------------------

class ProviderStatsSerializer(serializers.Serializer):
    tasks_inbox = serializers.IntegerField()
    active_tasks = serializers.IntegerField()
    completed_this_month = serializers.IntegerField()
    earnings_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)


class ProviderPendingTaskRowSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    task_ref = serializers.CharField()
    title = serializers.CharField()
    due_date = serializers.DateField(allow_null=True)
    estimated_hours = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    payout_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class ProviderActiveTaskRowSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    task_ref = serializers.CharField()
    service_client = serializers.CharField()
    progress = serializers.IntegerField()
    due_date = serializers.DateField(allow_null=True)
    status = serializers.CharField()


class ProviderEarningsSummarySerializer(serializers.Serializer):
    total_earned = serializers.DecimalField(max_digits=14, decimal_places=2)
    pending_payout = serializers.DecimalField(max_digits=12, decimal_places=2)
    tasks_total = serializers.IntegerField()
    accept_rate = serializers.FloatField()


class ProviderDeadlineRowSerializer(serializers.Serializer):
    task_ref = serializers.CharField()
    title = serializers.CharField()
    due_date = serializers.DateField(allow_null=True)
    days_remaining = serializers.IntegerField(allow_null=True)


class ProviderDashboardSerializer(serializers.Serializer):
    stats = ProviderStatsSerializer()
    pending_action_tasks = ProviderPendingTaskRowSerializer(many=True)
    active_tasks = ProviderActiveTaskRowSerializer(many=True)
    earnings_summary = ProviderEarningsSummarySerializer()
    upcoming_deadlines = ProviderDeadlineRowSerializer(many=True)


# ---------------------------------------------------------------------------
# ADMIN DASHBOARD  (GET /api/dashboard/admin)
# ---------------------------------------------------------------------------

class AdminStatsSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    active_orders = serializers.IntegerField()
    total_clients = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    unassigned_tasks = serializers.IntegerField()
    active_providers = serializers.IntegerField()
    rejected_tasks_last_7_days = serializers.IntegerField()


class AdminDashboardSerializer(serializers.Serializer):
    stats = AdminStatsSerializer()
    recent_orders = RecentOrderRowSerializer(many=True)
    unassigned_tasks = UnassignedTaskRowSerializer(many=True)
    revenue_by_service = RevenueByServiceRowSerializer(many=True)
    provider_availability = ProviderAvailabilityRowSerializer(many=True)


# ---------------------------------------------------------------------------
# FINANCE DASHBOARD  (GET /api/dashboard/finance)
# ---------------------------------------------------------------------------

class FinanceStatsSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    outstanding = serializers.DecimalField(max_digits=14, decimal_places=2)
    outstanding_invoice_count = serializers.IntegerField()
    total_expenses = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_margin_percent = serializers.FloatField()


class RecentInvoiceRowSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    invoice_number = serializers.CharField()
    client_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    due_date = serializers.DateField(allow_null=True)
    status = serializers.CharField()


class RecentBillRowSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    bill_number = serializers.CharField()
    vendor_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    due_date = serializers.DateField(allow_null=True)
    status = serializers.CharField()


class CashFlowSerializer(serializers.Serializer):
    inflow = serializers.DecimalField(max_digits=14, decimal_places=2)
    outflow = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    receivable = serializers.DecimalField(max_digits=14, decimal_places=2)
    payable = serializers.DecimalField(max_digits=14, decimal_places=2)


class TaxSummarySerializer(serializers.Serializer):
    gst_collected = serializers.DecimalField(max_digits=14, decimal_places=2)
    gst_paid = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_gst_liability = serializers.DecimalField(max_digits=14, decimal_places=2)
    tds_deducted = serializers.DecimalField(max_digits=14, decimal_places=2)


class FinanceDashboardSerializer(serializers.Serializer):
    stats = FinanceStatsSerializer()
    recent_invoices = RecentInvoiceRowSerializer(many=True)
    recent_bills = RecentBillRowSerializer(many=True)
    cash_flow = CashFlowSerializer()
    tax_summary = TaxSummarySerializer()