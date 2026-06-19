from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from .models import Provider, ProviderRating, ProviderPayout
from authentication.permissions import IsAdminOrSuperAdmin
from authentication.models import User

# ══════════════════════════════════════════════
# GET /api/providers/
# Admin lists all providers with filters
# ══════════════════════════════════════════════
class ProviderListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        providers = Provider.objects.filter(is_active=True)

        role_filter = request.query_params.get('role')
        availability_filter = request.query_params.get('availability')

        if role_filter:
            providers = providers.filter(role=role_filter)
        if availability_filter:
            providers = providers.filter(availability_status=availability_filter)

        data = []
        for p in providers:
            active_orders = p.user.assigned_orders.filter(status='Active').count()
            data.append({
                'id': str(p.id),
                'name': p.user.name,
                'email': p.user.email,
                'role': p.role,
                'specializations': p.specializations,
                'availability_status': p.availability_status,
                'active_orders': active_orders,
                'total_orders_completed': p.total_orders_completed,
                'avg_rating': p.avg_rating,
                'joined_date': p.joined_date,
            })

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/providers/
# Admin creates a new provider
# ══════════════════════════════════════════════
class ProviderCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        role = request.data.get('role', 'Other')
        specializations = request.data.get('specializations', [])
        qualifications = request.data.get('qualifications', '')
        bank_account_name = request.data.get('bank_account_name', '')
        bank_account_number = request.data.get('bank_account_number', '')
        bank_ifsc = request.data.get('bank_ifsc', '')
        commission_type = request.data.get('commission_type', 'percent')
        commission_value = request.data.get('commission_value', 0)

        if not name or not email or not phone:
            return Response({
                'success': False,
                'message': 'name, email and phone are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'A user with this email already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create user account with STAFF role
        import random, string
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        user = User.objects.create_user(
            email=email,
            name=name,
            phone=phone,
            password=temp_password
        )
        user.role = 'STAFF'
        user.save()

        provider = Provider.objects.create(
            user=user,
            role=role,
            specializations=specializations,
            qualifications=qualifications,
            bank_account_name=bank_account_name,
            bank_account_number=bank_account_number,
            bank_ifsc=bank_ifsc,
            commission_type=commission_type,
            commission_value=commission_value,
        )

        return Response({
            'success': True,
            'message': f'Provider {name} created successfully.',
            'data': {
                'id': str(provider.id),
                'name': user.name,
                'email': user.email,
                'role': provider.role,
                'temp_password': temp_password,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/providers/<id>/
# Get single provider profile with metrics
# ══════════════════════════════════════════════
class ProviderDetailView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, pk):
        provider = get_object_or_404(Provider, pk=pk)

        active_orders = provider.user.assigned_orders.filter(status='Active')
        active_orders_data = [{
            'order_number': o.order_number,
            'service_name': o.service.name if o.service else '',
            'status': o.status,
        } for o in active_orders]

        ratings = provider.ratings.all()[:5]
        ratings_data = [{
            'rating': r.rating,
            'feedback': r.feedback,
            'created_at': r.created_at,
        } for r in ratings]

        return Response({
            'success': True,
            'data': {
                'id': str(provider.id),
                'name': provider.user.name,
                'email': provider.user.email,
                'phone': provider.user.phone,
                'role': provider.role,
                'specializations': provider.specializations,
                'qualifications': provider.qualifications,
                'availability_status': provider.availability_status,
                'commission_type': provider.commission_type,
                'commission_value': str(provider.commission_value),
                'total_orders_completed': provider.total_orders_completed,
                'avg_completion_days': provider.avg_completion_days,
                'avg_rating': provider.avg_rating,
                'active_orders': active_orders_data,
                'recent_ratings': ratings_data,
                'joined_date': provider.joined_date,
                'is_active': provider.is_active,
            }
        })


# ══════════════════════════════════════════════
# PUT /api/providers/<id>/
# Admin updates provider profile
# ══════════════════════════════════════════════
class ProviderUpdateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        provider = get_object_or_404(Provider, pk=pk)

        provider.role = request.data.get('role', provider.role)
        provider.specializations = request.data.get('specializations', provider.specializations)
        provider.qualifications = request.data.get('qualifications', provider.qualifications)
        provider.bank_account_name = request.data.get('bank_account_name', provider.bank_account_name)
        provider.bank_account_number = request.data.get('bank_account_number', provider.bank_account_number)
        provider.bank_ifsc = request.data.get('bank_ifsc', provider.bank_ifsc)
        provider.commission_type = request.data.get('commission_type', provider.commission_type)
        provider.commission_value = request.data.get('commission_value', provider.commission_value)
        provider.save()

        # Update name/phone on user if provided
        name = request.data.get('name')
        phone = request.data.get('phone')
        if name:
            provider.user.name = name
        if phone:
            provider.user.phone = phone
        provider.user.save()

        return Response({
            'success': True,
            'message': 'Provider updated successfully.',
            'data': {
                'id': str(provider.id),
                'name': provider.user.name,
                'role': provider.role,
            }
        })

    def delete(self, request, pk):
        provider = get_object_or_404(Provider, pk=pk)
        provider.is_active = False
        provider.availability_status = 'Inactive'
        provider.save()
        return Response({
            'success': True,
            'message': f'Provider {provider.user.name} deactivated successfully.'
        })


# ══════════════════════════════════════════════
# POST /api/providers/<id>/activate/
# Admin activates a provider
# ══════════════════════════════════════════════
class ProviderActivateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        provider = get_object_or_404(Provider, pk=pk)
        provider.is_active = True
        provider.availability_status = 'Available'
        provider.save()

        return Response({
            'success': True,
            'message': f'Provider {provider.user.name} activated successfully.'
        })


# ══════════════════════════════════════════════
# POST /api/providers/<id>/deactivate/
# Admin deactivates a provider
# ══════════════════════════════════════════════
class ProviderDeactivateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        provider = get_object_or_404(Provider, pk=pk)
        provider.is_active = False
        provider.availability_status = 'Inactive'
        provider.save()

        return Response({
            'success': True,
            'message': f'Provider {provider.user.name} deactivated successfully.'
        })


# ══════════════════════════════════════════════
# GET /api/providers/availability/
# List all providers with real-time availability
# ══════════════════════════════════════════════
class ProviderAvailabilityView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]
    def get(self, request, pk):
        provider = get_object_or_404(Provider, pk=pk)
        active_count = provider.user.assigned_orders.filter(status='Active').count()
        return Response({
            'success': True,
            'data': {
                'id': str(provider.id),
                'name': provider.user.name,
                'role': provider.role,
                'availability_status': provider.availability_status,
                'active_orders_count': active_count,
            }
        })
        


# ══════════════════════════════════════════════
# GET /api/providers/earnings/
# Provider views their own earnings, Admin can filter by provider_id
# ══════════════════════════════════════════════
class ProviderEarningsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            # Specific provider earnings (via URL)
            provider = get_object_or_404(Provider, pk=pk)
        else:
            # Provider requesting their own earnings
            provider = get_object_or_404(Provider, user=request.user)

        payouts = ProviderPayout.objects.filter(provider=provider)

        total_earned = payouts.filter(status='Paid').aggregate(
            total=Sum('amount'))['total'] or 0
        pending_amount = payouts.filter(status='Pending').aggregate(
            total=Sum('amount'))['total'] or 0

        payout_history = [{
            'id': str(p.id),
            'order_number': p.order.order_number if p.order else None,
            'amount': str(p.amount),
            'status': p.status,
            'paid_at': p.paid_at,
            'created_at': p.created_at,
        } for p in payouts[:20]]

        return Response({
            'success': True,
            'data': {
                'provider_name': provider.user.name,
                'total_earned': str(total_earned),
                'pending_amount': str(pending_amount),
                'total_orders_completed': provider.total_orders_completed,
                'payout_history': payout_history,
            }
        })


# ══════════════════════════════════════════════
# GET /api/providers/tasks/
# Provider views tasks/orders assigned to them
# ══════════════════════════════════════════════
class ProviderTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):  # ← add pk=None
        if pk:
            provider = get_object_or_404(Provider, pk=pk)  # ← use pk, not query_param
            user = provider.user
        else:
            user = request.user

        orders = user.assigned_orders.all()

        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)

        data = [{
            'id': str(o.id),
            'order_number': o.order_number,
            'service_name': o.service.name if o.service else '',
            'client_name': o.client.name,
            'status': o.status,
            'expected_completion_date': o.expected_completion_date,
            'created_at': o.created_at,
        } for o in orders]

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })