from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from decimal import Decimal
from services.models import Service, Package
from payments.models import Coupon, CouponUsage
from orders.models import Order
from django.utils import timezone
import uuid

# ══════════════════════════════════════════════
# POST /api/checkout/validate/
# Validates service and package before checkout
# ══════════════════════════════════════════════
class ValidateCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        service_id = request.data.get('service_id')
        package_id = request.data.get('package_id')

        if not service_id or not package_id:
            return Response({
                'success': False,
                'message': 'service_id and package_id are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate service exists and is active
        try:
            service = Service.objects.get(pk=service_id, is_active=True)
        except Service.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Service not found or inactive.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Validate package belongs to service
        try:
            package = Package.objects.get(pk=package_id, service=service, is_active=True)
        except Package.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Package not found or does not belong to this service.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'message': 'Checkout details are valid.',
            'data': {
                'service': {
                    'id': str(service.id),
                    'name': service.name,
                    'category': service.category,
                },
                'package': {
                    'id': str(package.id),
                    'name': package.name,
                    'price': str(package.price),
                    'billing_period': package.billing_period,
                    'features': package.features,
                }
            }
        })


# ══════════════════════════════════════════════
# POST /api/checkout/calculate-tax/
# Calculates GST and total for order summary
# ══════════════════════════════════════════════
class CalculateTaxView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        package_id = request.data.get('package_id')
        coupon_code = request.data.get('coupon_code', None)
        use_wallet = request.data.get('use_wallet', False)

        if not package_id:
            return Response({
                'success': False,
                'message': 'package_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        package = get_object_or_404(Package, pk=package_id, is_active=True)

        base_amount = package.price
        gst_rate = Decimal('0.18')
        gst_amount = round(base_amount * gst_rate, 2)
        discount = Decimal('0')
        wallet_deduction = Decimal('0')
        coupon_applied = None

        # Apply coupon if provided
        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code.upper(),
                    is_active=True
                )
                # Check expiry
                if not coupon.expires_at or coupon.expires_at > timezone.now():
                    # Check usage limit
                    if coupon.used_count < coupon.usage_limit:
                        # Check user hasn't used it
                        already_used = CouponUsage.objects.filter(
                            coupon=coupon, user=request.user
                        ).exists()
                        if not already_used:
                            if coupon.discount_type == 'percent':
                                discount = (base_amount * coupon.discount_value) / Decimal('100')
                                if coupon.max_discount:
                                    discount = min(discount, coupon.max_discount)
                            else:
                                discount = coupon.discount_value
                            coupon_applied = coupon.code
            except Coupon.DoesNotExist:
                pass

        # Apply wallet balance if requested
        if use_wallet:
            available_wallet = request.user.wallet_balance
            subtotal_after_discount = base_amount - discount
            wallet_deduction = min(available_wallet, subtotal_after_discount)

        # Final calculations
        taxable_amount = base_amount - discount
        gst_amount = round(taxable_amount * gst_rate, 2)
        total = taxable_amount + gst_amount - wallet_deduction

        return Response({
            'success': True,
            'data': {
                'base_amount': str(base_amount),
                'discount': str(discount),
                'coupon_applied': coupon_applied,
                'taxable_amount': str(taxable_amount),
                'gst_rate': '18%',
                'gst_amount': str(gst_amount),
                'wallet_deduction': str(wallet_deduction),
                'wallet_balance': str(request.user.wallet_balance),
                'total': str(total),
                'currency': 'INR',
            }
        })


# ══════════════════════════════════════════════
# POST /api/checkout/create-order/
# Creates order after checkout form is filled
# ══════════════════════════════════════════════
class CheckoutCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        package_id = request.data.get('package_id')
        payment_method = request.data.get('payment_method', 'UPI')
        coupon_code = request.data.get('coupon_code', None)
        use_wallet = request.data.get('use_wallet', False)

        # Business details
        business_name = request.data.get('business_name', '')
        business_type = request.data.get('business_type', '')
        business_category = request.data.get('business_category', '')
        number_of_directors = request.data.get('number_of_directors', '')

        if not package_id:
            return Response({
                'success': False,
                'message': 'package_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        package = get_object_or_404(Package, pk=package_id, is_active=True)

        base_amount = package.price
        gst_rate = Decimal('0.18')
        discount = Decimal('0')
        wallet_deduction = Decimal('0')

        # Apply coupon
        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code.upper(),
                    is_active=True
                )
                already_used = CouponUsage.objects.filter(
                    coupon=coupon, user=request.user
                ).exists()
                if not already_used and coupon.used_count < coupon.usage_limit:
                    if coupon.discount_type == 'percent':
                        discount = (base_amount * coupon.discount_value) / Decimal('100')
                        if coupon.max_discount:
                            discount = min(discount, coupon.max_discount)
                    else:
                        discount = coupon.discount_value

                    # Mark coupon as used
                    CouponUsage.objects.create(coupon=coupon, user=request.user)
                    coupon.used_count += 1
                    coupon.save()
            except Coupon.DoesNotExist:
                pass

        # Apply wallet
        if use_wallet:
            available_wallet = request.user.wallet_balance
            subtotal_after_discount = base_amount - discount
            wallet_deduction = min(available_wallet, subtotal_after_discount)
            request.user.wallet_balance -= wallet_deduction
            request.user.save()

        # Calculate final amounts
        taxable_amount = base_amount - discount
        gst_amount = round(taxable_amount * gst_rate, 2)
        total_paid = taxable_amount + gst_amount - wallet_deduction

        # Default milestones
        DEFAULT_MILESTONES = [
            {"name": "Order Confirmed", "status": "completed"},
            {"name": "Documents Collected", "status": "pending"},
            {"name": "Work In Progress", "status": "pending"},
            {"name": "Review & Approval", "status": "pending"},
            {"name": "Completed & Delivered", "status": "pending"},
        ]

        # Create order
        order = Order.objects.create(
            client=request.user,
            service=package.service,
            package=package,
            base_amount=base_amount,
            gst_amount=gst_amount,
            discount=discount + wallet_deduction,
            total_paid=total_paid,
            payment_method=payment_method,
            milestones=DEFAULT_MILESTONES,
            business_name=business_name,
            business_type=business_type,
            business_category=business_category,
            number_of_directors=number_of_directors,
        )

        # Send notification
        try:
            from notifications.views import create_notification
            create_notification(
                user=request.user,
                title=f'Order {order.order_number} Created!',
                body=f'Your order for {package.service.name} - {package.name} has been created. Complete payment to activate.',
                notification_type='ORDER_UPDATE',
                related_order_id=order.id
            )
        except Exception as e:
            print(f"Notification error: {e}")

        return Response({
            'success': True,
            'message': f'Order {order.order_number} created successfully!',
            'data': {
                'order_id': str(order.id),
                'order_number': order.order_number,
                'service': package.service.name,
                'package': package.name,
                'base_amount': str(base_amount),
                'discount': str(discount + wallet_deduction),
                'gst_amount': str(gst_amount),
                'total_paid': str(total_paid),
                'payment_method': payment_method,
                'status': order.status,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# POST /api/checkout/apply-coupon/
# Validates and previews coupon discount
# ══════════════════════════════════════════════
class CheckoutApplyCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        package_id = request.data.get('package_id')

        if not code or not package_id:
            return Response({
                'success': False,
                'message': 'code and package_id are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        package = get_object_or_404(Package, pk=package_id, is_active=True)

        try:
            coupon = Coupon.objects.get(code=code.upper(), is_active=True)
        except Coupon.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid or expired coupon code.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check expiry
        if coupon.expires_at and coupon.expires_at < timezone.now():
            return Response({
                'success': False,
                'message': 'This coupon has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check usage limit
        if coupon.used_count >= coupon.usage_limit:
            return Response({
                'success': False,
                'message': 'This coupon has reached its usage limit.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already used it
        already_used = CouponUsage.objects.filter(
            coupon=coupon, user=request.user
        ).exists()
        if already_used:
            return Response({
                'success': False,
                'message': 'You have already used this coupon.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate discount
        base_amount = package.price
        if coupon.discount_type == 'percent':
            discount = (base_amount * coupon.discount_value) / Decimal('100')
            if coupon.max_discount:
                discount = min(discount, coupon.max_discount)
        else:
            discount = coupon.discount_value

        return Response({
            'success': True,
            'message': f'Coupon {coupon.code} applied successfully!',
            'data': {
                'code': coupon.code,
                'discount_type': coupon.discount_type,
                'discount_value': str(coupon.discount_value),
                'discount_amount': str(discount),
                'new_total': str(base_amount - discount),
            }
        })


# ══════════════════════════════════════════════
# POST /api/checkout/remove-coupon/
# Removes applied coupon from checkout
# ══════════════════════════════════════════════
class CheckoutRemoveCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        package_id = request.data.get('package_id')

        if not package_id:
            return Response({
                'success': False,
                'message': 'package_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        package = get_object_or_404(Package, pk=package_id, is_active=True)
        base_amount = package.price
        gst_amount = round(base_amount * Decimal('0.18'), 2)
        total = base_amount + gst_amount

        return Response({
            'success': True,
            'message': 'Coupon removed successfully.',
            'data': {
                'base_amount': str(base_amount),
                'discount': '0.00',
                'gst_amount': str(gst_amount),
                'total': str(total),
            }
        })