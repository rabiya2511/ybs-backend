from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from .models import Expense
from .serializers import ExpenseSerializer, ExpenseCreateSerializer
from authentication.permissions import IsAdminOrSuperAdmin


# ══════════════════════════════════════════════
# GET /api/expenses/
# POST /api/expenses/
# ══════════════════════════════════════════════
class ExpenseListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        # Admin sees all, client sees own
        if request.user.role in ('SUPER_ADMIN', 'STAFF', 'FINANCE_ADMIN'):
            expenses = Expense.objects.all()
        else:
            expenses = Expense.objects.filter(created_by=request.user)

        # Filters
        category = request.query_params.get('category')
        status_filter = request.query_params.get('status')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')

        if category:
            expenses = expenses.filter(category=category)
        if status_filter:
            expenses = expenses.filter(status=status_filter)
        if from_date:
            expenses = expenses.filter(expense_date__gte=from_date)
        if to_date:
            expenses = expenses.filter(expense_date__lte=to_date)

        total = expenses.aggregate(
            total=Sum('amount'))['total'] or 0

        serializer = ExpenseSerializer(expenses, many=True)
        return Response({
            'success': True,
            'count': expenses.count(),
            'total_amount': str(total),
            'data': serializer.data
        })

    def post(self, request):
        serializer = ExpenseCreateSerializer(data=request.data)
        if serializer.is_valid():
            expense = serializer.save(created_by=request.user)

            # Handle receipt upload
            receipt = request.FILES.get('receipt')
            if receipt:
                expense.receipt = receipt
                expense.save()

            return Response({
                'success': True,
                'message': 'Expense created successfully.',
                'data': ExpenseSerializer(expense).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════
# GET /api/expenses/<id>/
# PUT /api/expenses/<id>/
# DELETE /api/expenses/<id>/
# ══════════════════════════════════════════════
class ExpenseDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk)
        return Response({
            'success': True,
            'data': ExpenseSerializer(expense).data
        })

    def put(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk)

        # Only creator or admin can update
        if expense.created_by != request.user and request.user.role not in ('SUPER_ADMIN', 'STAFF', 'FINANCE_ADMIN'):
            return Response({
                'success': False,
                'message': 'You do not have permission to update this expense.'
            }, status=status.HTTP_403_FORBIDDEN)

        if expense.status == 'Approved':
            return Response({
                'success': False,
                'message': 'Cannot update an approved expense.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ExpenseCreateSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            expense = serializer.save()

            # Handle receipt upload
            receipt = request.FILES.get('receipt')
            if receipt:
                expense.receipt = receipt
                expense.save()

            return Response({
                'success': True,
                'message': 'Expense updated successfully.',
                'data': ExpenseSerializer(expense).data
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk)

        # Only creator or admin can delete
        if expense.created_by != request.user and request.user.role not in ('SUPER_ADMIN', 'STAFF', 'FINANCE_ADMIN'):
            return Response({
                'success': False,
                'message': 'You do not have permission to delete this expense.'
            }, status=status.HTTP_403_FORBIDDEN)

        if expense.status == 'Approved':
            return Response({
                'success': False,
                'message': 'Cannot delete an approved expense.'
            }, status=status.HTTP_400_BAD_REQUEST)

        expense.delete()
        return Response({
            'success': True,
            'message': 'Expense deleted successfully.'
        })