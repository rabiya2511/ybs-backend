from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import ServiceCategory
from authentication.permissions import IsAdminOrSuperAdmin
from rest_framework.permissions import IsAuthenticated

# ══════════════════════════════════════════════
# GET /api/categories/
# Public — list all active categories
# ══════════════════════════════════════════════
class CategoryListView(APIView):
    def get(self, request):
        categories = ServiceCategory.objects.filter(is_active=True)
        data = []
        for c in categories:
            data.append({
                'id': str(c.id),
                'name': c.name,
                'slug': c.slug,
                'description': c.description,
                'icon': c.icon,
                'sort_order': c.sort_order,
            })
        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/categories/
# Admin — create new category
# ══════════════════════════════════════════════
class CategoryCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        name = request.data.get('name')
        slug = request.data.get('slug')
        description = request.data.get('description', '')
        icon = request.data.get('icon', 'x')
        sort_order = request.data.get('sort_order', 0)

        if not name or not slug:
            return Response({
                'success': False,
                'message': 'name and slug are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if ServiceCategory.objects.filter(name=name).exists():
            return Response({
                'success': False,
                'message': 'Category with this name already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)

        category = ServiceCategory.objects.create(
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            sort_order=sort_order,
        )

        return Response({
            'success': True,
            'message': f'Category {category.name} created successfully.',
            'data': {
                'id': str(category.id),
                'name': category.name,
                'slug': category.slug,
            }
        }, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════
# GET /api/categories/<id>/
# Public — get single category
# ══════════════════════════════════════════════
class CategoryDetailView(APIView):
    def get(self, request, pk):
        category = get_object_or_404(ServiceCategory, pk=pk, is_active=True)
        return Response({
            'success': True,
            'data': {
                'id': str(category.id),
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'icon': category.icon,
                'sort_order': category.sort_order,
            }
        })


# ══════════════════════════════════════════════
# PUT /api/categories/<id>/
# Admin — update category
# ══════════════════════════════════════════════
class CategoryUpdateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, pk):
        category = get_object_or_404(ServiceCategory, pk=pk)

        category.name = request.data.get('name', category.name)
        category.slug = request.data.get('slug', category.slug)
        category.description = request.data.get('description', category.description)
        category.icon = request.data.get('icon', category.icon)
        category.sort_order = request.data.get('sort_order', category.sort_order)
        category.is_active = request.data.get('is_active', category.is_active)
        category.save()

        return Response({
            'success': True,
            'message': f'Category {category.name} updated successfully.',
            'data': {
                'id': str(category.id),
                'name': category.name,
                'slug': category.slug,
                'is_active': category.is_active,
            }
        })

    def delete(self, request, pk):
        category = get_object_or_404(ServiceCategory, pk=pk)
        category.is_active = False
        category.save()
        return Response({
            'success': True,
            'message': f'Category {category.name} deactivated successfully.'
        })