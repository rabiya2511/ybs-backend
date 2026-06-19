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
# ══════════════════════════════════════════════
# DELETE /api/services/admin/<id>/delete/
# Admin deletes a service
# ══════════════════════════════════════════════
class ServiceDeleteView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def delete(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        service_name = service.name
        service.delete()
        return Response({
            'success': True,
            'message': f'Service "{service_name}" deleted successfully.'
        })


# ══════════════════════════════════════════════
# DELETE /api/services/admin/packages/<id>/delete/
# Admin deletes a package
# ══════════════════════════════════════════════
class PackageDeleteView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def delete(self, request, pk):
        package = get_object_or_404(Package, pk=pk)
        package_name = package.name
        package.delete()
        return Response({
            'success': True,
            'message': f'Package "{package_name}" deleted successfully.'
        })


# ══════════════════════════════════════════════
# GET /api/services/featured/
# List featured services
# ══════════════════════════════════════════════
class FeaturedServicesView(APIView):
    permission_classes = []

    def get(self, request):
        services = Service.objects.filter(is_featured=True, is_active=True)
        data = []
        for s in services:
           data.append({
                'id': str(s.id),
                'name': s.name,
                'category': s.category,
                'description': s.description[:100] if s.description else '',
                'icon': s.icon,
                'is_featured': s.is_featured,
                'starting_price': str(s.starting_price),
            })
        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# GET /api/services/popular/
# List popular services (by order count)
# ══════════════════════════════════════════════
class PopularServicesView(APIView):
    permission_classes = []

    def get(self, request):
        from django.db.models import Count
        services = Service.objects.filter(
            is_active=True
        ).annotate(
            order_count=Count('packages')
        ).order_by('-order_count')[:6]

        data = []
        for s in services:
            data.append({
                'id': str(s.id),
                'name': s.name,
                'category': s.category,
                'short_description': s.description[:100] if s.description else '',
                'icon': s.icon,
                'starting_price': str(s.starting_price),
            })
        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# GET /api/services/category/<category>/
# List services by category
# ══════════════════════════════════════════════
class ServicesByCategoryView(APIView):
    permission_classes = []

    def get(self, request, category):
        services = Service.objects.filter(
            category=category,
            is_active=True
        )
        data = []
        for s in services:
            data.append({
                'id': str(s.id),
                'name': s.name,
                'category': s.category,
                'description': s.description[:100] if s.description else '',
                'icon': s.icon,
                'starting_price': str(s.starting_price),
            })
        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# GET /api/services/<id>/packages/
# List packages for a specific service
# ══════════════════════════════════════════════
class ServicePackagesView(APIView):
    permission_classes = []

    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        packages = Package.objects.filter(service=service, is_active=True)
        data = []
        for p in packages:
            data.append({
                'id': str(p.id),
                'name': p.name,
                'price': str(p.price),
                'gst_rate': str(p.gst_rate),
                'delivery_days': p.delivery_days,
                'features': p.features,
                'is_popular': p.is_popular,
            })
        return Response({
            'success': True,
            'service': service.name,
            'count': len(data),
            'data': data
        })
# ══════════════════════════════════════════════
# POST /api/services/admin/bulk-upload/
# Admin bulk uploads multiple services at once
# ══════════════════════════════════════════════
class ServiceBulkUploadView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        services_data = request.data.get('services')

        if not services_data or not isinstance(services_data, list):
            return Response({
                'success': False,
                'message': 'services must be a non-empty list of service objects.'
            }, status=status.HTTP_400_BAD_REQUEST)

        created = []
        errors = []

        for index, item in enumerate(services_data):
            name = item.get('name')
            category = item.get('category')
            starting_price = item.get('starting_price')

            if not name or not category or starting_price is None:
                errors.append({
                    'index': index,
                    'message': 'name, category and starting_price are required.'
                })
                continue

            service = Service.objects.create(
                name=name,
                category=category,
                description=item.get('description', ''),
                icon=item.get('icon', ''),
                starting_price=starting_price,
                is_active=item.get('is_active', True),
                is_featured=item.get('is_featured', False),
            )
            created.append({
                'id': str(service.id),
                'name': service.name,
                'category': service.category,
            })

        return Response({
            'success': True,
            'message': f'{len(created)} services created, {len(errors)} failed.',
            'created': created,
            'errors': errors,
        }, status=status.HTTP_201_CREATED)