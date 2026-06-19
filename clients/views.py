from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import ClientNote, ClientAccountManager
from authentication.models import User
from authentication.permissions import IsAdminOrSuperAdmin

# ══════════════════════════════════════════════
# GET /api/clients/
# Admin lists all clients with search
# ══════════════════════════════════════════════
class ClientListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        clients = User.objects.filter(role='CLIENT')

        search = request.query_params.get('search')
        status_filter = request.query_params.get('status')

        if search:
            from django.db.models import Q
            clients = clients.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(company_name__icontains=search)
            )
        if status_filter:
            clients = clients.filter(status=status_filter)

        data = []
        for c in clients:
            data.append({
                'id': str(c.id),
                'name': c.name,
                'email': c.email,
                'phone': c.phone,
                'company_name': c.company_name,
                'status': c.status,
                'created_at': c.created_at,
            })

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/clients/
# Admin creates a new client account manually
# ══════════════════════════════════════════════
class ClientCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        company_name = request.data.get('company_name', '')

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

        import random, string
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        client = User.objects.create_user(
            email=email,
            name=name,
            phone=phone,
            password=temp_password
        )
        client.company_name = company_name
        client.save()

        return Response({
            'success': True,
            'message': f'Client {name} created successfully.',
            'data': {
                'id': str(client.id),
                'name': client.name,
                'email': client.email,
                'temp_password': temp_password,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/clients/<id>/
# Admin views full client profile
# ══════════════════════════════════════════════
class ClientDetailView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, pk):
        client = get_object_or_404(User, pk=pk, role='CLIENT')

        notes = client.admin_notes.all()[:10]
        notes_data = [{
            'id': n.id,
            'note': n.note,
            'created_by': n.created_by.name if n.created_by else None,
            'created_at': n.created_at,
        } for n in notes]

        manager_link = ClientAccountManager.objects.filter(client=client).first()

        return Response({
            'success': True,
            'data': {
                'id': str(client.id),
                'name': client.name,
                'email': client.email,
                'phone': client.phone,
                'company_name': client.company_name,
                'gstin': client.gstin,
                'pan': client.pan,
                'status': client.status,
                'wallet_balance': str(client.wallet_balance),
                'referral_code': client.referral_code,
                'is_verified': client.is_verified,
                'account_manager': manager_link.manager.name if manager_link and manager_link.manager else None,
                'notes': notes_data,
                'created_at': client.created_at,
            }
        })


# ══════════════════════════════════════════════
# PUT /api/clients/<id>/
# Admin updates client profile
# ══════════════════════════════════════════════
class ClientUpdateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        client = get_object_or_404(User, pk=pk, role='CLIENT')

        client.name = request.data.get('name', client.name)
        client.phone = request.data.get('phone', client.phone)
        client.company_name = request.data.get('company_name', client.company_name)
        client.gstin = request.data.get('gstin', client.gstin)
        client.pan = request.data.get('pan', client.pan)
        client.save()

        return Response({
            'success': True,
            'message': 'Client updated successfully.',
            'data': {
                'id': str(client.id),
                'name': client.name,
                'company_name': client.company_name,
            }
        })

    def delete(self, request, pk):
        client = get_object_or_404(User, pk=pk, role='CLIENT')
        client.status = 'INACTIVE'
        client.is_active = False
        client.save()
        return Response({
            'success': True,
            'message': f'Client {client.name} deactivated successfully.'
        })


# ══════════════════════════════════════════════
# POST /api/clients/<id>/suspend/
# Admin suspends a client account
# ══════════════════════════════════════════════
class ClientSuspendView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        client = get_object_or_404(User, pk=pk, role='CLIENT')
        client.status = 'SUSPENDED'
        client.save()

        reason = request.data.get('reason', '')
        if reason:
            ClientNote.objects.create(
                client=client,
                note=f"Account suspended. Reason: {reason}",
                created_by=request.user
            )

        return Response({
            'success': True,
            'message': f'Client {client.name} suspended successfully.'
        })


# ══════════════════════════════════════════════
# POST /api/clients/<id>/activate/
# Admin reactivates a suspended client
# ══════════════════════════════════════════════
class ClientActivateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        client = get_object_or_404(User, pk=pk, role='CLIENT')
        client.status = 'ACTIVE'
        client.is_active = True
        client.save()

        return Response({
            'success': True,
            'message': f'Client {client.name} reactivated successfully.'
        })


# ══════════════════════════════════════════════
# GET /api/clients/<id>/orders/
# Admin views all orders by this client
# ══════════════════════════════════════════════
class ClientOrdersView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, pk):
        client = get_object_or_404(User, pk=pk, role='CLIENT')
        orders = client.orders.all()

        data = [{
            'id': str(o.id),
            'order_number': o.order_number,
            'service_name': o.service.name if o.service else '',
            'package_name': o.package.name if o.package else '',
            'total_paid': str(o.total_paid),
            'status': o.status,
            'created_at': o.created_at,
        } for o in orders]

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# GET /api/clients/<id>/projects/
# Admin views all projects for this client
# ══════════════════════════════════════════════
class ClientProjectsView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, pk):
        client = get_object_or_404(User, pk=pk, role='CLIENT')
        projects = client.projects.all()

        data = [{
            'id': str(p.id),
            'title': p.title,
            'status': p.status,
            'progress': p.progress,
            'order_number': p.order.order_number,
            'expected_completion_date': p.expected_completion_date,
        } for p in projects]

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# GET /api/clients/<id>/invoices/
# Admin views all invoices for this client
# ══════════════════════════════════════════════
class ClientInvoicesView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, pk):
        client = get_object_or_404(User, pk=pk, role='CLIENT')
        invoices = client.invoices.all()

        data = [{
            'id': str(i.id),
            'invoice_number': i.invoice_number,
            'total': str(i.total),
            'status': i.status,
            'due_date': i.due_date,
            'paid_at': i.paid_at,
        } for i in invoices]

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })