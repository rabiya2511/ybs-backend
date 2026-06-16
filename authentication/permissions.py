from rest_framework.permissions import BasePermission

class IsAdminOrSuperAdmin(BasePermission):
    """
    Only allows STAFF, FINANCE_ADMIN or SUPER_ADMIN to access
    """
    message = 'Access denied. You do not have permission to perform this action.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['STAFF', 'FINANCE_ADMIN', 'SUPER_ADMIN']


class IsSuperAdmin(BasePermission):
    """
    Only allows SUPER_ADMIN to access
    """
    message = 'Access denied. Super Admin only.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'SUPER_ADMIN'


class IsFinanceAdmin(BasePermission):
    """
    Only allows FINANCE_ADMIN or SUPER_ADMIN to access
    """
    message = 'Access denied. Finance Admin only.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['FINANCE_ADMIN', 'SUPER_ADMIN']


class IsClient(BasePermission):
    """
    Only allows CLIENT role to access
    """
    message = 'Access denied. Clients only.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'CLIENT'