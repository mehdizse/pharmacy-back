from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission accordée uniquement aux administrateurs
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin
        )


class IsPharmacienOrAdmin(permissions.BasePermission):
    """
    Permission accordée aux pharmaciens et administrateurs
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_pharmacien or request.user.is_admin)
        )


class IsComptableOrAdmin(permissions.BasePermission):
    """
    Permission accordée aux comptables et administrateurs
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_comptable or request.user.is_admin)
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission accordée uniquement au propriétaire de l'objet
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user == request.user


class IsFinanceUser(permissions.BasePermission):
    """
    Permission accordée aux utilisateurs ayant accès aux données financières
    (Comptables, Pharmaciens, Admins)
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_comptable or 
             request.user.is_pharmacien or 
             request.user.is_admin)
        )
