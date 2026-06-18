from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.shortcuts import get_object_or_404
import random

from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer,
    OTPSendSerializer, OTPVerifySerializer,
    ResetPasswordSerializer, UserProfileSerializer
)

def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['SUPER_ADMIN', 'STAFF']

# ─── AUTH APIs ───────────────────────────────────────────

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens(user)
            return Response({
                'message': 'Account created successfully',
                'tokens': tokens,
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if not user:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            if user.status == 'SUSPENDED':
                return Response({'error': 'Your account has been suspended'}, status=status.HTTP_403_FORBIDDEN)
            tokens = get_tokens(user)
            return Response({
                'message': 'Login successful',
                'tokens': tokens,
                'user': UserProfileSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPSendView(APIView):
    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            if not User.objects.filter(phone=phone).exists():
                return Response({'error': 'No account found with this phone number'}, status=status.HTTP_404_NOT_FOUND)
            otp = str(random.randint(100000, 999999))
            cache.set(f'otp_{phone}', otp, timeout=300)
            print(f'OTP for {phone}: {otp}')
            return Response({'message': 'OTP sent successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            otp = serializer.validated_data['otp']
            cached_otp = cache.get(f'otp_{phone}')
            if not cached_otp or cached_otp != otp:
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
            cache.delete(f'otp_{phone}')
            user = User.objects.get(phone=phone)
            user.is_verified = True
            user.save()
            tokens = get_tokens(user)
            return Response({
                'message': 'OTP verified successfully',
                'tokens': tokens,
                'user': UserProfileSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            cached_otp = cache.get(f'otp_{phone}')
            if not cached_otp or cached_otp != otp:
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
            cache.delete(f'otp_{phone}')
            user = User.objects.get(phone=phone)
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


# ─── USER PROFILE APIs (Client) ──────────────────────────

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'Profile fetched successfully',
            'user': UserProfileSerializer(request.user).data
        })

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.user.is_active = False
        request.user.status = 'INACTIVE'
        request.user.save()
        return Response({'message': 'Account deactivated successfully'})


# ─── ADMIN USER MANAGEMENT APIs ──────────────────────────

class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-created_at')
        # filter by status if provided
        status_filter = request.query_params.get('status')
        role_filter = request.query_params.get('role')
        search = request.query_params.get('search')
        if status_filter:
            users = users.filter(status=status_filter)
        if role_filter:
            users = users.filter(role=role_filter)
        if search:
            users = users.filter(name__icontains=search) | users.filter(email__icontains=search)
        serializer = UserProfileSerializer(users, many=True)
        return Response({
            'message': 'Users fetched successfully',
            'count': users.count(),
            'users': serializer.data
        })

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # allow admin to set role
            role = request.data.get('role', 'CLIENT')
            user.role = role
            user.save()
            return Response({
                'message': 'User created successfully',
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        return Response({
            'message': 'User fetched successfully',
            'user': UserProfileSerializer(user).data
        })

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'User updated successfully',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response({'message': 'User deleted successfully'})


class AdminUserStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        new_status = request.data.get('status')
        if new_status not in ['ACTIVE', 'INACTIVE', 'SUSPENDED']:
            return Response({'error': 'Invalid status. Use ACTIVE, INACTIVE or SUSPENDED'}, status=status.HTTP_400_BAD_REQUEST)
        user.status = new_status
        user.save()
        return Response({
            'message': f'User status updated to {new_status}',
            'user': UserProfileSerializer(user).data
        })
from .models import PasswordResetToken, EmailVerificationToken
from django.utils import timezone
from datetime import timedelta
import secrets

# ══════════════════════════════════════════════
# POST /api/auth/forgot-password/
# Request a password reset token
# ══════════════════════════════════════════════
class ForgotPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                'success': False,
                'message': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response({
                'success': True,
                'message': 'If this email exists, a reset token has been sent.'
            })

        # Invalidate old tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

        # Create new token
        token = secrets.token_urlsafe(32)
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=1)
        )

        # In production send email, for now return token in response
        return Response({
            'success': True,
            'message': 'Password reset token generated.',
            'reset_token': token,  # Remove this in production
            'expires_in': '1 hour'
        })


# ══════════════════════════════════════════════
# POST /api/auth/confirm-reset-password/
# Reset password using token
# ══════════════════════════════════════════════
class ConfirmResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not token or not new_password:
            return Response({
                'success': False,
                'message': 'token and new_password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                is_used=False
            )
        except PasswordResetToken.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid or already used token.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check expiry
        if reset_token.expires_at < timezone.now():
            return Response({
                'success': False,
                'message': 'Token has expired. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user = reset_token.user
        user.set_password(new_password)
        user.save()

        # Mark token as used
        reset_token.is_used = True
        reset_token.save()

        return Response({
            'success': True,
            'message': 'Password reset successfully. Please login with your new password.'
        })


# ══════════════════════════════════════════════
# POST /api/auth/change-password/
# Change password while logged in
# ══════════════════════════════════════════════
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response({
                'success': False,
                'message': 'current_password and new_password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check current password
        if not request.user.check_password(current_password):
            return Response({
                'success': False,
                'message': 'Current password is incorrect.'
            }, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()

        return Response({
            'success': True,
            'message': 'Password changed successfully. Please login again.'
        })


# ══════════════════════════════════════════════
# POST /api/auth/verify-email/
# Verify email with token
# ══════════════════════════════════════════════
class VerifyEmailView(APIView):
    permission_classes = []

    def post(self, request):
        token = request.data.get('token')

        if not token:
            return Response({
                'success': False,
                'message': 'token is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification = EmailVerificationToken.objects.get(
                token=token,
                is_used=False
            )
        except EmailVerificationToken.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid or already used token.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if verification.expires_at < timezone.now():
            return Response({
                'success': False,
                'message': 'Token has expired. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Mark user as verified
        user = verification.user
        user.is_verified = True
        user.save()

        # Mark token as used
        verification.is_used = True
        verification.save()

        return Response({
            'success': True,
            'message': 'Email verified successfully.'
        })


# ══════════════════════════════════════════════
# POST /api/auth/resend-verification/
# Resend email verification token
# ══════════════════════════════════════════════
class ResendVerificationView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                'success': False,
                'message': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': True,
                'message': 'If this email exists, a verification token has been sent.'
            })

        if user.is_verified:
            return Response({
                'success': False,
                'message': 'Email is already verified.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Invalidate old tokens
        EmailVerificationToken.objects.filter(user=user, is_used=False).update(is_used=True)

        # Create new token
        token = secrets.token_urlsafe(32)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24)
        )

        return Response({
            'success': True,
            'message': 'Verification token generated.',
            'verification_token': token,  # Remove this in production
            'expires_in': '24 hours'
        })


# ══════════════════════════════════════════════
# DELETE /api/auth/account/
# Delete own account
# ══════════════════════════════════════════════
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        password = request.data.get('password')

        if not password:
            return Response({
                'success': False,
                'message': 'Please confirm your password to delete account.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(password):
            return Response({
                'success': False,
                'message': 'Incorrect password.'
            }, status=status.HTTP_400_BAD_REQUEST)

        request.user.delete()

        return Response({
            'success': True,
            'message': 'Account deleted successfully.'
        })    