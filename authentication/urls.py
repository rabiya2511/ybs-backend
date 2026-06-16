from django.urls import path
from .views import (
    RegisterView, LoginView,
    OTPSendView, OTPVerifyView,
    ResetPasswordView, ProfileView,
    LogoutView,
    AdminUserListView, AdminUserDetailView,
    AdminUserStatusView
)

urlpatterns = [
    # Auth APIs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('otp/send/', OTPSendView.as_view(), name='otp-send'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # User Profile APIs
    path('profile/', ProfileView.as_view(), name='profile'),

    # Admin User Management APIs
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<uuid:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<uuid:user_id>/status/', AdminUserStatusView.as_view(), name='admin-user-status'),
]