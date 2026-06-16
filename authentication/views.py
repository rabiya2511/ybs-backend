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