from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ResetPasswordView,
    OTPSendView,
    OTPVerifyView,
    AdminUserListView,
    AdminUserDetailView,
    AdminUserStatusView,
    ForgotPasswordView,
    ConfirmResetPasswordView,
    ChangePasswordView,
    VerifyEmailView,
    ResendVerificationView,
    DeleteAccountView,
)

urlpatterns = [
    # ── Core Auth ─────────────────────────────
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # ── Password Management ───────────────────
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('confirm-reset-password/', ConfirmResetPasswordView.as_view(), name='confirm-reset-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    # ── Email Verification ────────────────────
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),

    # ── Account ───────────────────────────────
    path('account/', DeleteAccountView.as_view(), name='delete-account'),

    # ── OTP ───────────────────────────────────
    path('otp/send/', OTPSendView.as_view(), name='otp-send'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),

    # ── Admin ─────────────────────────────────
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<uuid:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<uuid:user_id>/status/', AdminUserStatusView.as_view(), name='admin-user-status'),
]