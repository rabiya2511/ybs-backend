"""
Role-based permission classes for the four dashboard endpoints.

Role values come from authentication.models.User.ROLE_CHOICES:
    CLIENT, STAFF, FINANCE_ADMIN, SUPER_ADMIN

Admin dashboard is open to: SUPER_ADMIN, STAFF, FINANCE_ADMIN

Provider access is NOT determined by `role` (there's no PROVIDER role in
ROLE_CHOICES) but by whether the user has a linked Provider profile
(providers.models.Provider.user OneToOne, related_name='provider_profile').
"""
from rest_framework.permissions import BasePermission


class IsClientUser(BasePermission):
    """Any authenticated client can view their own dashboard."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'CLIENT'
        )


class IsProviderUser(BasePermission):
    """User must have a linked Provider profile to view the provider dashboard."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'provider_profile')
        )


class IsAdminPanelUser(BasePermission):
    """Admin dashboard: Super Admin, Staff, and Finance Admin."""

    ALLOWED_ROLES = {'SUPER_ADMIN', 'STAFF', 'FINANCE_ADMIN'}

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ALLOWED_ROLES
        )


class IsFinanceUser(BasePermission):
    """
    Finance dashboard: Super Admin and Finance Admin always.
    Staff/Providers only if explicitly granted Books access later.
    """

    ALLOWED_ROLES = {'SUPER_ADMIN', 'FINANCE_ADMIN'}

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role in self.ALLOWED_ROLES:
            return True
        # TODO: once a BooksAccess model exists, check
        # BooksAccess.objects.filter(user=request.user, access_granted=True,
        # scope='full').exists() here to allow scoped staff/providers in.
        return False