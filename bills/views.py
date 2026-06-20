from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from .models import Bill
from .serializers import BillSerializer, BillCreateSerializer
from authentication.permissions import IsAdminOrSuperAdmin


# ══════════════════════════════════════════════
# GET /api/bills/
# POST /api/bills/
# ══════════════════════════════════════════════
class BillListCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        bills = Bill.objects.all()

        # Filters
        status_filter  = request.query_params.get('status')
        category       = request.query_params.get('category')
        from_date      = request.query_params.get('from')
        to_date        = request.query_params.get('to')

        if status_filter:
            bills = bills.filter(status=status_filter)
        if category:
            bills = bills.filter(category=category)
        if from_date:
            bills = bills.filter(bill_date__gte=from_date)
        if to_date:
            bills = bills.filter(bill_date__lte=to_date)

        total = bills.aggregate(
            total=Sum('total_amount'))['total'] or 0

        serializer = BillSerializer(bills, many=True)
        return Response({
            'success': True,
            'count': bills.count(),
            'total_amount': str(total),
            'data': serializer.data
        })

    def post(self, request):
        serializer = BillCreateSerializer(data=request.data)
        if serializer.is_valid():
            bill = serializer.save(created_by=request.user)

            # Calculate total
            bill.total_amount = bill.amount + bill.gst_amount
            
            # Handle attachment
            attachment = request.FILES.get('attachment')
            if attachment:
                bill.attachment = attachment
            bill.save()

            return Response({
                'success': True,
                'message': f'Bill {bill.bill_number} created successfully.',
                'data': BillSerializer(bill).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════
# GET /api/bills/<id>/
# PUT /api/bills/<id>/
# DELETE /api/bills/<id>/
# ══════════════════════════════════════════════
class BillDetailView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        bill = get_object_or_404(Bill, pk=pk)
        return Response({
            'success': True,
            'data': BillSerializer(bill).data
        })

    def put(self, request, pk):
        bill = get_object_or_404(Bill, pk=pk)

        if bill.status == 'Approved':
            return Response({
                'success': False,
                'message': 'Cannot update an approved bill.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = BillCreateSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            bill = serializer.save()
            bill.total_amount = bill.amount + bill.gst_amount

            attachment = request.FILES.get('attachment')
            if attachment:
                bill.attachment = attachment
            bill.save()

            return Response({
                'success': True,
                'message': f'Bill {bill.bill_number} updated successfully.',
                'data': BillSerializer(bill).data
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = get_object_or_404(Bill, pk=pk)

        if bill.status == 'Approved':
            return Response({
                'success': False,
                'message': 'Cannot delete an approved bill.'
            }, status=status.HTTP_400_BAD_REQUEST)

        bill.delete()
        return Response({
            'success': True,
            'message': f'Bill {bill.bill_number} deleted successfully.'
        })


# ══════════════════════════════════════════════
# POST /api/bills/approve/
# ══════════════════════════════════════════════
class BillApproveView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        bill_id = request.data.get('bill_id')
        notes   = request.data.get('notes', '')

        if not bill_id:
            return Response({
                'success': False,
                'message': 'bill_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        bill = get_object_or_404(Bill, pk=bill_id)

        if bill.status == 'Approved':
            return Response({
                'success': False,
                'message': 'Bill is already approved.'
            }, status=status.HTTP_400_BAD_REQUEST)

        bill.status      = 'Approved'
        bill.approved_by = request.user
        bill.approved_at = timezone.now()
        if notes:
            bill.notes = notes
        bill.save()

        return Response({
            'success': True,
            'message': f'Bill {bill.bill_number} approved successfully.',
            'data': BillSerializer(bill).data
        })