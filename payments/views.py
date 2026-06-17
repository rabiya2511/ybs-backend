from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal
import uuid
from .models import Payment, Coupon, CouponUsage
from orders.models import Order
from authentication.permissions import IsAdminOrSuperAdmin


# ══════════════════════════════════════════════
# POST /api/payments/initiate/
# ══════════════════════════════════════════════
class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method', 'UPI')

        if not order_id:
            return Response({
                'success': False,
                'message': 'order_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Convert to UUID
        try:
            order_uuid = uuid.UUID(str(order_id))
        except (ValueError, AttributeError):
            return Response({
                'success': False,
                'message': 'Invalid order_id format.'
            }, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, pk=order_uuid, client=request.user)

        existing = Payment.objects.filter(order=order, status='Success').first()
        if existing:
            return Response({
                'success': False,
                'message': 'This order has already been paid.'
            }, status=status.HTTP_400_BAD_REQUEST)

        transaction_id = 'TXN' + uuid.uuid4().hex[:12].upper()

        payment = Payment.objects.create(
            order=order,
            client=request.user,
            amount=order.base_amount,
            gst_amount=order.gst_amount,
            total_amount=order.total_paid,
            payment_method=payment_method,
            transaction_id=transaction_id,
            status='Pending'
        )

        return Response({
            'success': True,
            'message': 'Payment initiated successfully.',
            'data': {
                'payment_id': str(payment.id),
                'transaction_id': transaction_id,
                'amount': str(payment.total_amount),
                'currency': 'INR',
                'order_number': order.order_number,
                'payment_method': payment_method,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# POST /api/payments/confirm/
# ══════════════════════════════════════════════
class ConfirmPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        transaction_id = request.data.get('transaction_id')

        if not payment_id or not transaction_id:
            return Response({
                'success': False,
                'message': 'payment_id and transaction_id are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Convert to UUID
        try:
            payment_uuid = uuid.UUID(str(payment_id))
        except (ValueError, AttributeError):
            return Response({
                'success': False,
                'message': 'Invalid payment_id format.'
            }, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(
            Payment,
            pk=payment_uuid,
            client=request.user,
            transaction_id=transaction_id
        )

        if payment.status == 'Success':
            return Response({
                'success': False,
                'message': 'Payment already confirmed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Mark payment successful
        payment.status = 'Success'
        payment.save()

        # Activate order
        order = payment.order
        order.status = 'Active'
        order.save()

        # Auto generate invoice
        try:
            from accounting.models import Invoice
            Invoice.objects.create(
                invoice_number='INV-' + str(order.order_number).replace('YBS-', ''),
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
                status='Paid',
                paid_at=timezone.now(),
                due_date=timezone.now().date(),
            )
        except Exception as e:
            print(f"Invoice creation error: {e}")

        return Response({
            'success': True,
            'message': 'Payment confirmed! Your order is now active.',
            'data': {
                'transaction_id': payment.transaction_id,
                'order_number': order.order_number,
                'order_status': order.status,
                'amount_paid': str(payment.total_amount),
                'payment_method': payment.payment_method,
            }
        })


# ══════════════════════════════════════════════
# GET /api/payments/my-payments/
# ══════════════════════════════════════════════
class MyPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(client=request.user)
        data = []
        for p in payments:
            data.append({
                'id': str(p.id),
                'transaction_id': p.transaction_id,
                'order_number': p.order.order_number,
                'service_name': p.order.service.name if p.order.service else '',
                'amount': str(p.total_amount),
                'payment_method': p.payment_method,
                'status': p.status,
                'created_at': p.created_at,
            })
        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# GET /api/payments/admin/
# ══════════════════════════════════════════════
class AdminPaymentListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        payments = Payment.objects.all()
        status_filter = request.query_params.get('status')
        if status_filter:
            payments = payments.filter(status=status_filter)

        data = []
        for p in payments:
            data.append({
                'id': str(p.id),
                'transaction_id': p.transaction_id,
                'order_number': p.order.order_number,
                'client_name': p.client.name,
                'client_email': p.client.email,
                'service_name': p.order.service.name if p.order.service else '',
                'amount': str(p.total_amount),
                'payment_method': p.payment_method,
                'status': p.status,
                'created_at': p.created_at,
            })

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/payments/admin/<id>/refund/
# ══════════════════════════════════════════════
class AdminRefundView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)

        if payment.status != 'Success':
            return Response({
                'success': False,
                'message': 'Only successful payments can be refunded.'
            }, status=status.HTTP_400_BAD_REQUEST)

        refund_amount = request.data.get('refund_amount', payment.total_amount)
        refund_reason = request.data.get('refund_reason', '')

        payment.status = 'Refunded'
        payment.refund_amount = Decimal(str(refund_amount))
        payment.refund_reason = refund_reason
        payment.refunded_at = timezone.now()
        payment.refund_id = 'RFD' + uuid.uuid4().hex[:10].upper()
        payment.save()

        order = payment.order
        order.status = 'Cancelled'
        order.save()

        return Response({
            'success': True,
            'message': 'Refund processed successfully.',
            'data': {
                'refund_id': payment.refund_id,
                'refund_amount': str(payment.refund_amount),
                'order_number': order.order_number,
                'order_status': order.status,
            }
        })


# ══════════════════════════════════════════════
# POST /api/payments/apply-coupon/
# ══════════════════════════════════════════════
class ApplyCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        order_amount = request.data.get('order_amount')

        if not code or not order_amount:
            return Response({
                'success': False,
                'message': 'code and order_amount are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(code=code.upper(), is_active=True)
        except Coupon.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid or expired coupon code.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if coupon.expires_at and coupon.expires_at < timezone.now():
            return Response({
                'success': False,
                'message': 'This coupon has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if coupon.used_count >= coupon.usage_limit:
            return Response({
                'success': False,
                'message': 'This coupon has reached its usage limit.'
            }, status=status.HTTP_400_BAD_REQUEST)

        already_used = CouponUsage.objects.filter(
            coupon=coupon, user=request.user
        ).exists()
        if already_used:
            return Response({
                'success': False,
                'message': 'You have already used this coupon.'
            }, status=status.HTTP_400_BAD_REQUEST)

        order_amount = Decimal(str(order_amount))
        if order_amount < coupon.min_order_amount:
            return Response({
                'success': False,
                'message': f'Minimum order amount is ₹{coupon.min_order_amount}.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if coupon.discount_type == 'percent':
            discount = (order_amount * coupon.discount_value) / Decimal('100')
            if coupon.max_discount:
                discount = min(discount, coupon.max_discount)
        else:
            discount = coupon.discount_value

        final_amount = order_amount - discount

        # Save usage and increment counter
        CouponUsage.objects.create(coupon=coupon, user=request.user)
        coupon.used_count += 1
        coupon.save()

        return Response({
            'success': True,
            'message': 'Coupon applied successfully!',
            'data': {
                'code': coupon.code,
                'discount_type': coupon.discount_type,
                'discount_value': str(coupon.discount_value),
                'discount_amount': str(discount),
                'original_amount': str(order_amount),
                'final_amount': str(final_amount),
            }
        })


# ══════════════════════════════════════════════
# GET /api/payments/wallet/
# ══════════════════════════════════════════════
class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'success': True,
            'data': {
                'wallet_balance': str(request.user.wallet_balance),
                'currency': 'INR',
            }
        })


# ══════════════════════════════════════════════
# POST /api/payments/wallet/use/
# ══════════════════════════════════════════════
class UseWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        amount_to_use = request.data.get('amount')

        if not order_id or not amount_to_use:
            return Response({
                'success': False,
                'message': 'order_id and amount are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Convert to UUID
        try:
            order_uuid = uuid.UUID(str(order_id))
        except (ValueError, AttributeError):
            return Response({
                'success': False,
                'message': 'Invalid order_id format.'
            }, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, pk=order_uuid, client=request.user)
        amount_to_use = Decimal(str(amount_to_use))

        if request.user.wallet_balance < amount_to_use:
            return Response({
                'success': False,
                'message': f'Insufficient wallet balance. Available: ₹{request.user.wallet_balance}'
            }, status=status.HTTP_400_BAD_REQUEST)

        request.user.wallet_balance -= amount_to_use
        request.user.save()

        order.discount += amount_to_use
        order.total_paid -= amount_to_use
        order.save()

        return Response({
            'success': True,
            'message': f'₹{amount_to_use} wallet balance applied successfully.',
            'data': {
                'amount_used': str(amount_to_use),
                'remaining_wallet_balance': str(request.user.wallet_balance),
                'new_order_total': str(order.total_paid),
            }
        })


# ══════════════════════════════════════════════
# POST /api/payments/admin/coupons/create/
# ══════════════════════════════════════════════
class AdminCreateCouponView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        code = request.data.get('code', '').upper()
        discount_type = request.data.get('discount_type', 'percent')
        discount_value = request.data.get('discount_value')
        min_order_amount = request.data.get('min_order_amount', 0)
        max_discount = request.data.get('max_discount', None)
        usage_limit = request.data.get('usage_limit', 1)
        expires_at = request.data.get('expires_at', None)

        if not code or not discount_value:
            return Response({
                'success': False,
                'message': 'code and discount_value are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Coupon.objects.filter(code=code).exists():
            return Response({
                'success': False,
                'message': 'Coupon code already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)

        coupon = Coupon.objects.create(
            code=code,
            discount_type=discount_type,
            discount_value=Decimal(str(discount_value)),
            min_order_amount=Decimal(str(min_order_amount)),
            max_discount=Decimal(str(max_discount)) if max_discount else None,
            usage_limit=usage_limit,
            expires_at=expires_at,
        )

        return Response({
            'success': True,
            'message': f'Coupon {coupon.code} created successfully.',
            'data': {
                'id': coupon.id,
                'code': coupon.code,
                'discount_type': coupon.discount_type,
                'discount_value': str(coupon.discount_value),
                'usage_limit': coupon.usage_limit,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/payments/admin/coupons/
# ══════════════════════════════════════════════
class AdminCouponListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        coupons = Coupon.objects.all().order_by('-created_at')
        data = []
        for c in coupons:
            data.append({
                'id': c.id,
                'code': c.code,
                'discount_type': c.discount_type,
                'discount_value': str(c.discount_value),
                'min_order_amount': str(c.min_order_amount),
                'usage_limit': c.usage_limit,
                'used_count': c.used_count,
                'is_active': c.is_active,
                'expires_at': c.expires_at,
            })
        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })