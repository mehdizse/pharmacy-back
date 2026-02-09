"""
Custom permissions for invoices with ownership checks
"""
from rest_framework.permissions import BasePermission
from django.core.exceptions import PermissionDenied


class CanAccessInvoice(BasePermission):
    """
    Lecture: admin OK, finance OK uniquement si supplier dans UserSupplierAccess
    """

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return user.is_admin or user.is_comptable or user.is_pharmacien

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True

        supplier = getattr(obj, "supplier", None)
        if not supplier:
            return False

        from apps.suppliers.models import UserSupplierAccess
        return UserSupplierAccess.objects.filter(
            user=user,
            supplier=supplier
        ).exists()


class CanModifyInvoice(BasePermission):
    """
    Écriture: admin only (et éventuellement règles métier)
    """

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_admin)

    def has_object_permission(self, request, view, obj):
        # Admin only
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)
