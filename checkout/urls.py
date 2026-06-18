from django.urls import path
from .views import (
    ValidateCheckoutView,
    CalculateTaxView,
    CheckoutCreateOrderView,
    CheckoutApplyCouponView,
    CheckoutRemoveCouponView,
)

urlpatterns = [
    # Validate service and package before checkout
    path('validate/', ValidateCheckoutView.as_view(), name='checkout-validate'),
    # Calculate tax and total for order summary
    path('calculate-tax/', CalculateTaxView.as_view(), name='calculate-tax'),
    # Create order after checkout form filled
    path('create-order/', CheckoutCreateOrderView.as_view(), name='checkout-create-order'),
    # Apply coupon code
    path('apply-coupon/', CheckoutApplyCouponView.as_view(), name='checkout-apply-coupon'),
    # Remove coupon code
    path('remove-coupon/', CheckoutRemoveCouponView.as_view(), name='checkout-remove-coupon'),
]