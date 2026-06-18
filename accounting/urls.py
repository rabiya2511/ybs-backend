from django.urls import path
from .views import (
    MyInvoicesView,
    InvoiceDetailView,
    MarkInvoicePaidView,
    SendInvoiceView,
    AdminInvoiceListView,
    AdminCreateInvoiceView,
    AdminUpdateInvoiceView,
    AdminDeleteInvoiceView,
    AdminExpenseListView,
    AdminAddExpenseView,
    AdminUpdateExpenseView,
    AdminDeleteExpenseView,
    AdminBillListView,
    AdminAddBillView,
    AdminUpdateBillView,
    AdminDeleteBillView,
    ApproveBillView,
    AdminFinancialSummaryView,
    ProfitLossReportView,
    GSTReportView,
    MonthlySummaryReportView,
)

urlpatterns = [
    # ── Client Routes ─────────────────────────────
    path('invoices/', MyInvoicesView.as_view(), name='my-invoices'),
    path('invoices/<uuid:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/<uuid:pk>/mark-paid/', MarkInvoicePaidView.as_view(), name='mark-invoice-paid'),
    path('invoices/<uuid:pk>/send/', SendInvoiceView.as_view(), name='send-invoice'),

    # ── Admin Invoice Routes ───────────────────────
    path('admin/invoices/', AdminInvoiceListView.as_view(), name='admin-invoices'),
    path('admin/invoices/create/', AdminCreateInvoiceView.as_view(), name='admin-create-invoice'),
    path('admin/invoices/<uuid:pk>/', AdminUpdateInvoiceView.as_view(), name='admin-update-invoice'),
    path('admin/invoices/<uuid:pk>/delete/', AdminDeleteInvoiceView.as_view(), name='admin-delete-invoice'),

    # ── Admin Expense Routes ───────────────────────
    path('admin/expenses/', AdminExpenseListView.as_view(), name='admin-expenses'),
    path('admin/expenses/add/', AdminAddExpenseView.as_view(), name='admin-add-expense'),
    path('admin/expenses/<uuid:pk>/', AdminUpdateExpenseView.as_view(), name='admin-update-expense'),
    path('admin/expenses/<uuid:pk>/delete/', AdminDeleteExpenseView.as_view(), name='admin-delete-expense'),

    # ── Admin Bill Routes ──────────────────────────
    path('admin/bills/', AdminBillListView.as_view(), name='admin-bills'),
    path('admin/bills/add/', AdminAddBillView.as_view(), name='admin-add-bill'),
    path('admin/bills/<uuid:pk>/', AdminUpdateBillView.as_view(), name='admin-update-bill'),
    path('admin/bills/<uuid:pk>/delete/', AdminDeleteBillView.as_view(), name='admin-delete-bill'),
    path('admin/bills/<uuid:pk>/approve/', ApproveBillView.as_view(), name='admin-approve-bill'),

    # ── Reports ────────────────────────────────────
    path('admin/summary/', AdminFinancialSummaryView.as_view(), name='admin-financial-summary'),
    path('admin/reports/profit-loss/', ProfitLossReportView.as_view(), name='profit-loss-report'),
    path('admin/reports/gst/', GSTReportView.as_view(), name='gst-report'),
    path('admin/reports/monthly-summary/', MonthlySummaryReportView.as_view(), name='monthly-summary-report'),
]