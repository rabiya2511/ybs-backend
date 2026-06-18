from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal
from .models import Invoice, Bill, Expense
from authentication.permissions import IsAdminOrSuperAdmin


# ══════════════════════════════════════════════
# GET /api/accounting/invoices/
# Client views their invoices
# ══════════════════════════════════════════════
class MyInvoicesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invoices = Invoice.objects.filter(client=request.user)
        data = []
        for inv in invoices:
            data.append({
                'id': str(inv.id),
                'invoice_number': inv.invoice_number,
                'order_number': inv.order.order_number if inv.order else '',
                'subtotal': str(inv.subtotal),
                'gst_amount': str(inv.gst_amount),
                'discount': str(inv.discount),
                'total': str(inv.total),
                'status': inv.status,
                'issue_date': inv.issue_date,
                'due_date': inv.due_date,
                'paid_at': inv.paid_at,
                'created_at': inv.created_at,
            })
        return Response({'success': True, 'count': len(data), 'data': data})


# ══════════════════════════════════════════════
# GET /api/accounting/invoices/<id>/
# Client views single invoice
# ══════════════════════════════════════════════
class InvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk, client=request.user)
        return Response({
            'success': True,
            'data': {
                'id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'order_number': invoice.order.order_number if invoice.order else '',
                'client_name': invoice.client.name,
                'client_email': invoice.client.email,
                'line_items': invoice.line_items,
                'subtotal': str(invoice.subtotal),
                'gst_amount': str(invoice.gst_amount),
                'discount': str(invoice.discount),
                'total': str(invoice.total),
                'status': invoice.status,
                'issue_date': invoice.issue_date,
                'due_date': invoice.due_date,
                'paid_at': invoice.paid_at,
                'notes': invoice.notes,
                'created_at': invoice.created_at,
            }
        })


# ══════════════════════════════════════════════
# POST /api/accounting/invoices/<id>/mark-paid/
# Mark invoice as paid
# ══════════════════════════════════════════════
class MarkInvoicePaidView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        if invoice.status == 'Paid':
            return Response({
                'success': False,
                'message': 'Invoice is already paid.'
            }, status=status.HTTP_400_BAD_REQUEST)
        invoice.status = 'Paid'
        invoice.paid_at = timezone.now()
        invoice.save()
        return Response({
            'success': True,
            'message': f'Invoice {invoice.invoice_number} marked as paid.'
        })


# ══════════════════════════════════════════════
# POST /api/accounting/invoices/<id>/send/
# Send invoice to client
# ══════════════════════════════════════════════
class SendInvoiceView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice.status = 'Sent'
        invoice.save()
        return Response({
            'success': True,
            'message': f'Invoice {invoice.invoice_number} marked as sent.'
        })


# ══════════════════════════════════════════════
# GET /api/accounting/admin/invoices/
# Admin views all invoices
# ══════════════════════════════════════════════
class AdminInvoiceListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        invoices = Invoice.objects.all()
        status_filter = request.query_params.get('status')
        if status_filter:
            invoices = invoices.filter(status=status_filter)
        data = []
        for inv in invoices:
            data.append({
                'id': str(inv.id),
                'invoice_number': inv.invoice_number,
                'client_name': inv.client.name,
                'client_email': inv.client.email,
                'order_number': inv.order.order_number if inv.order else '',
                'total': str(inv.total),
                'status': inv.status,
                'due_date': inv.due_date,
                'paid_at': inv.paid_at,
                'created_at': inv.created_at,
            })
        return Response({'success': True, 'count': len(data), 'data': data})


# ══════════════════════════════════════════════
# POST /api/accounting/admin/invoices/create/
# Admin manually creates invoice
# ══════════════════════════════════════════════
class AdminCreateInvoiceView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        from orders.models import Order
        order_id = request.data.get('order_id')
        due_date = request.data.get('due_date')
        notes = request.data.get('notes', '')

        if not order_id or not due_date:
            return Response({
                'success': False,
                'message': 'order_id and due_date are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, pk=order_id)

        if Invoice.objects.filter(order=order).exists():
            return Response({
                'success': False,
                'message': 'Invoice already exists for this order.'
            }, status=status.HTTP_400_BAD_REQUEST)

        count = Invoice.objects.count() + 1
        invoice = Invoice.objects.create(
            invoice_number=f'INV-{str(count).zfill(4)}',
            order=order,
            client=order.client,
            line_items=[{
                'description': f"{order.service.name} - {order.package.name}",
                'quantity': 1,
                'rate': str(order.base_amount),
                'amount': str(order.base_amount),
            }],
            subtotal=order.base_amount,
            gst_amount=order.gst_amount,
            discount=order.discount,
            total=order.total_paid,
            due_date=due_date,
            notes=notes,
            status='Draft',
        )

        return Response({
            'success': True,
            'message': 'Invoice created successfully.',
            'data': {
                'id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'total': str(invoice.total),
                'status': invoice.status,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/accounting/admin/expenses/
# Admin views all expenses
# ══════════════════════════════════════════════
class AdminExpenseListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        expenses = Expense.objects.all()
        category_filter = request.query_params.get('category')
        if category_filter:
            expenses = expenses.filter(category=category_filter)
        data = []
        for e in expenses:
            data.append({
                'id': str(e.id),
                'date': e.date,
                'category': e.category,
                'description': e.description,
                'amount': str(e.amount),
                'gst_amount': str(e.gst_amount),
                'paid_by': e.paid_by,
                'created_at': e.created_at,
            })
        return Response({'success': True, 'count': len(data), 'data': data})


# ══════════════════════════════════════════════
# POST /api/accounting/admin/expenses/add/
# Admin adds expense
# ══════════════════════════════════════════════
class AdminAddExpenseView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        date = request.data.get('date')
        category = request.data.get('category')
        description = request.data.get('description')
        amount = request.data.get('amount')
        paid_by = request.data.get('paid_by', '')

        if not date or not category or not description or not amount:
            return Response({
                'success': False,
                'message': 'date, category, description and amount are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        expense = Expense.objects.create(
            date=date,
            category=category,
            description=description,
            amount=Decimal(str(amount)),
            paid_by=paid_by,
        )

        return Response({
            'success': True,
            'message': 'Expense added successfully.',
            'data': {
                'id': str(expense.id),
                'category': expense.category,
                'amount': str(expense.amount),
                'date': expense.date,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/accounting/admin/bills/
# Admin views all bills
# ══════════════════════════════════════════════
class AdminBillListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        bills = Bill.objects.all()
        data = []
        for b in bills:
            data.append({
                'id': str(b.id),
                'bill_number': b.bill_number,
                'vendor_name': b.vendor_name,
                'category': b.category,
                'amount': str(b.amount),
                'due_date': b.due_date,
                'status': b.status,
                'paid_at': b.paid_at,
                'created_at': b.created_at,
            })
        return Response({'success': True, 'count': len(data), 'data': data})


# ══════════════════════════════════════════════
# POST /api/accounting/admin/bills/add/
# Admin adds a bill
# ══════════════════════════════════════════════
class AdminAddBillView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        vendor_name = request.data.get('vendor_name')
        category = request.data.get('category')
        amount = request.data.get('amount')
        due_date = request.data.get('due_date')
        notes = request.data.get('notes', '')

        if not vendor_name or not category or not amount or not due_date:
            return Response({
                'success': False,
                'message': 'vendor_name, category, amount and due_date are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        bill = Bill.objects.create(
            vendor_name=vendor_name,
            category=category,
            amount=Decimal(str(amount)),
            due_date=due_date,
            notes=notes,
        )

        return Response({
            'success': True,
            'message': 'Bill added successfully.',
            'data': {
                'id': str(bill.id),
                'bill_number': bill.bill_number,
                'vendor_name': bill.vendor_name,
                'amount': str(bill.amount),
                'due_date': bill.due_date,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/accounting/admin/summary/
# Financial summary
# ══════════════════════════════════════════════
class AdminFinancialSummaryView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        from django.db.models import Sum

        total_revenue = Invoice.objects.filter(
            status='Paid'
        ).aggregate(total=Sum('total'))['total'] or 0

        total_expenses = Expense.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_gst = Invoice.objects.filter(
            status='Paid'
        ).aggregate(total=Sum('gst_amount'))['total'] or 0

        pending_invoices = Invoice.objects.filter(
            status__in=['Sent', 'Overdue', 'Due']
        ).aggregate(total=Sum('total'))['total'] or 0

        pending_bills = Bill.objects.filter(
            status='Pending'
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'success': True,
            'data': {
                'total_revenue': str(total_revenue),
                'total_expenses': str(total_expenses),
                'net_profit': str(Decimal(str(total_revenue)) - Decimal(str(total_expenses))),
                'total_gst_collected': str(total_gst),
                'pending_invoices_amount': str(pending_invoices),
                'pending_bills_amount': str(pending_bills),
            }
        })
# ══════════════════════════════════════════════
# PUT /api/accounting/admin/invoices/<id>/
# Update invoice
# ══════════════════════════════════════════════
class AdminUpdateInvoiceView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice.notes = request.data.get('notes', invoice.notes)
        invoice.due_date = request.data.get('due_date', invoice.due_date)
        invoice.status = request.data.get('status', invoice.status)
        invoice.save()
        return Response({
            'success': True,
            'message': 'Invoice updated successfully.',
            'data': {
                'id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'status': invoice.status,
                'due_date': invoice.due_date,
            }
        })


# ══════════════════════════════════════════════
# DELETE /api/accounting/admin/invoices/<id>/
# Delete invoice
# ══════════════════════════════════════════════
class AdminDeleteInvoiceView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def delete(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice_number = invoice.invoice_number
        invoice.delete()
        return Response({
            'success': True,
            'message': f'Invoice {invoice_number} deleted successfully.'
        })


# ══════════════════════════════════════════════
# POST /api/accounting/admin/bills/<id>/approve/
# Approve a bill
# ══════════════════════════════════════════════
class ApproveBillView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        bill = get_object_or_404(Bill, pk=pk)
        if bill.status == 'Paid':
            return Response({
                'success': False,
                'message': 'Bill is already paid.'
            }, status=status.HTTP_400_BAD_REQUEST)
        bill.status = 'Paid'
        bill.paid_at = timezone.now()
        bill.save()
        return Response({
            'success': True,
            'message': f'Bill {bill.bill_number} approved and marked as paid.'
        })


# ══════════════════════════════════════════════
# PUT /api/accounting/admin/bills/<id>/
# Update bill
# ══════════════════════════════════════════════
class AdminUpdateBillView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        bill = get_object_or_404(Bill, pk=pk)
        bill.vendor_name = request.data.get('vendor_name', bill.vendor_name)
        bill.category = request.data.get('category', bill.category)
        bill.amount = request.data.get('amount', bill.amount)
        bill.due_date = request.data.get('due_date', bill.due_date)
        bill.notes = request.data.get('notes', bill.notes)
        bill.save()
        return Response({
            'success': True,
            'message': 'Bill updated successfully.',
            'data': {'id': str(bill.id), 'bill_number': bill.bill_number}
        })


# ══════════════════════════════════════════════
# DELETE /api/accounting/admin/bills/<id>/
# Delete bill
# ══════════════════════════════════════════════
class AdminDeleteBillView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def delete(self, request, pk):
        bill = get_object_or_404(Bill, pk=pk)
        bill_number = bill.bill_number
        bill.delete()
        return Response({
            'success': True,
            'message': f'Bill {bill_number} deleted successfully.'
        })


# ══════════════════════════════════════════════
# PUT /api/accounting/admin/expenses/<id>/
# Update expense
# ══════════════════════════════════════════════
class AdminUpdateExpenseView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk)
        expense.category = request.data.get('category', expense.category)
        expense.description = request.data.get('description', expense.description)
        expense.amount = request.data.get('amount', expense.amount)
        expense.date = request.data.get('date', expense.date)
        expense.paid_by = request.data.get('paid_by', expense.paid_by)
        expense.save()
        return Response({
            'success': True,
            'message': 'Expense updated successfully.',
            'data': {'id': str(expense.id), 'amount': str(expense.amount)}
        })


# ══════════════════════════════════════════════
# DELETE /api/accounting/admin/expenses/<id>/
# Delete expense
# ══════════════════════════════════════════════
class AdminDeleteExpenseView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def delete(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk)
        expense.delete()
        return Response({
            'success': True,
            'message': 'Expense deleted successfully.'
        })


# ══════════════════════════════════════════════
# GET /api/accounting/admin/reports/profit-loss/
# P&L Report
# ══════════════════════════════════════════════
class ProfitLossReportView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        from django.db.models import Sum
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        invoices = Invoice.objects.filter(status='Paid')
        expenses = Expense.objects.all()

        if month and year:
            invoices = invoices.filter(paid_at__month=month, paid_at__year=year)
            expenses = expenses.filter(date__month=month, date__year=year)

        revenue = invoices.aggregate(total=Sum('total'))['total'] or 0
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        profit = Decimal(str(revenue)) - Decimal(str(total_expenses))

        return Response({
            'success': True,
            'data': {
                'revenue': str(revenue),
                'expenses': str(total_expenses),
                'profit': str(profit),
                'month': month,
                'year': year,
            }
        })


# ══════════════════════════════════════════════
# GET /api/accounting/admin/reports/gst/
# GST Report
# ══════════════════════════════════════════════
class GSTReportView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        from django.db.models import Sum
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        invoices = Invoice.objects.filter(status='Paid')
        if month and year:
            invoices = invoices.filter(paid_at__month=month, paid_at__year=year)

        total_gst = invoices.aggregate(total=Sum('gst_amount'))['total'] or 0
        total_revenue = invoices.aggregate(total=Sum('subtotal'))['total'] or 0

        return Response({
            'success': True,
            'data': {
                'total_revenue_excluding_gst': str(total_revenue),
                'total_gst_collected': str(total_gst),
                'month': month,
                'year': year,
            }
        })


# ══════════════════════════════════════════════
# GET /api/accounting/admin/reports/monthly-summary/
# Monthly Summary
# ══════════════════════════════════════════════
class MonthlySummaryReportView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        from django.db.models import Sum, Count
        from django.db.models.functions import TruncMonth

        monthly = Invoice.objects.filter(
            status='Paid'
        ).annotate(
            month=TruncMonth('paid_at')
        ).values('month').annotate(
            revenue=Sum('total'),
            invoice_count=Count('id')
        ).order_by('-month')[:12]

        data = []
        for m in monthly:
            data.append({
                'month': m['month'].strftime('%Y-%m') if m['month'] else '',
                'revenue': str(m['revenue']),
                'invoice_count': m['invoice_count'],
            })

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })