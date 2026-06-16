from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Service, Package
from .serializers import (
    ServiceSerializer,
    ServiceCreateSerializer,
    PackageSerializer,
    PackageCreateSerializer,
)
from authentication.permissions import IsAdminOrSuperAdmin

# ══════════════════════════════════════════════
# GET /api/services/
# Public — clients browse all active services
# ══════════════════════════════════════════════
class ServiceListView(APIView):
    def get(self, request):
        category = request.query_params.get('category', None)
        services = Service.objects.filter(is_active=True)

        if category:
            services = services.filter(category=category)

        serializer = ServiceSerializer(services, many=True)
        return Response({
            'success': True,
            'count': services.count(),
            'data': serializer.data
        })

# ══════════════════════════════════════════════
# GET /api/services/<id>/
# Public — get single service with its packages
# ══════════════════════════════════════════════
class ServiceDetailView(APIView):
    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)  # removed is_active=True
        serializer = ServiceSerializer(service)
        return Response({
            'success': True,
            'data': serializer.data
        })
# ══════════════════════════════════════════════
# Admin only — Create service
# POST /api/services/admin/create/
# ══════════════════════════════════════════════
class ServiceCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        serializer = ServiceCreateSerializer(data=request.data)
        if serializer.is_valid():
            service = serializer.save()
            return Response({
                'success': True,
                'message': 'Service created successfully.',
                'data': ServiceSerializer(service).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# ══════════════════════════════════════════════
# Admin only — Edit or Delete service
# PUT /api/services/admin/<id>/update/
# DELETE /api/services/admin/<id>/update/
# ══════════════════════════════════════════════
class ServiceUpdateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        serializer = ServiceCreateSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            service = serializer.save()
            return Response({
                'success': True,
                'message': 'Service updated successfully.',
                'data': ServiceSerializer(service).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        service.is_active = False  # soft delete — don't remove from DB
        service.save()
        return Response({
            'success': True,
            'message': 'Service deactivated successfully.'
        })

# ══════════════════════════════════════════════
# Admin only — Create package for a service
# POST /api/services/admin/packages/create/
# ══════════════════════════════════════════════
class PackageCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        serializer = PackageCreateSerializer(data=request.data)
        if serializer.is_valid():
            package = serializer.save()
            return Response({
                'success': True,
                'message': 'Package created successfully.',
                'data': PackageSerializer(package).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# ══════════════════════════════════════════════
# Admin only — Edit or Delete package
# PUT /api/services/admin/packages/<id>/update/
# DELETE /api/services/admin/packages/<id>/update/
# ══════════════════════════════════════════════
class PackageUpdateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        package = get_object_or_404(Package, pk=pk)
        serializer = PackageCreateSerializer(package, data=request.data, partial=True)
        if serializer.is_valid():
            package = serializer.save()
            return Response({
                'success': True,
                'message': 'Package updated successfully.',
                'data': PackageSerializer(package).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        package = get_object_or_404(Package, pk=pk)
        package.delete()
        return Response({
            'success': True,
            'message': 'Package deleted successfully.'
        })