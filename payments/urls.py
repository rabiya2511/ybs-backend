from django.urls import path
from .views import (
    InitiatePaymentView,
    ConfirmPaymentView,
    MyPaymentsView,
    AdminPaymentListView,
    AdminRefundView,
    ApplyCouponView,
    WalletView,
    UseWalletView,
    AdminCreateCouponView,
    AdminCouponListView,
    TransactionListView,
    TransactionDetailView,
    VerifyPaymentView,
    RazorpayWebhookView,
    StripeWebhookView,
)

urlpatterns = [
    # ── Client Routes ─────────────────────────────
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('confirm/', ConfirmPaymentView.as_view(), name='confirm-payment'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('my-payments/', MyPaymentsView.as_view(), name='my-payments'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('transactions/<uuid:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('apply-coupon/', ApplyCouponView.as_view(), name='apply-coupon'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('wallet/use/', UseWalletView.as_view(), name='use-wallet'),

    # ── Webhooks ──────────────────────────────────
    path('webhook/razorpay/', RazorpayWebhookView.as_view(), name='razorpay-webhook'),
    path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),

    # ── Admin Routes ──────────────────────────────
    path('admin/', AdminPaymentListView.as_view(), name='admin-payments'),
    path('admin/<uuid:pk>/refund/', AdminRefundView.as_view(), name='admin-refund'),
    path('admin/coupons/', AdminCouponListView.as_view(), name='admin-coupons'),
    path('admin/coupons/create/', AdminCreateCouponView.as_view(), name='admin-create-coupon'),
]