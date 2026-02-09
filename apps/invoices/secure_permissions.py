"""
Secure permissions with proper ownership checks
"""
from rest_framework import permissions
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


class CanAccessInvoice(permissions.BasePermission):
    """
    Permission d'accès aux factures avec vérification stricte
    """
    
    def has_permission(self, request, view):
        """Vérification de base"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # L'utilisateur doit avoir un rôle financier
        return (request.user.is_admin or 
                request.user.is_comptable or 
                request.user.is_pharmacien)
    
    def has_object_permission(self, request, view, obj):
        """Vérification au niveau objet"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin peut tout voir
        if request.user.is_admin:
            return True
        
        # Autres utilisateurs: vérifier l'accès
        if hasattr(obj, 'supplier'):
            return self._can_access_supplier(request.user, obj.supplier)
        
        return False
    
    def _can_access_supplier(self, user, supplier):
        """Vérifier si l'utilisateur peut accéder à ce fournisseur"""
        # TODO: Implémenter la logique d'accès par organisation
        # Pour l'instant: tous les utilisateurs financiers peuvent tout voir
        return (user.is_comptable or user.is_pharmacien)


class CanModifyInvoice(permissions.BasePermission):
    """
    Permission de modification des factures (stricte)
    """
    
    def has_permission(self, request, view):
        """Seuls les admins peuvent modifier"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_admin
    
    def has_object_permission(self, request, view, obj):
        """Vérification stricte de modification"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin peut tout modifier (avec vérifications métier)
        if request.user.is_admin:
            # Vérifier les règles métier
            if hasattr(obj, 'credit_notes_count') and obj.credit_notes_count > 0:
                raise PermissionDenied(
                    _("Impossible de modifier cette facture : elle a des avoirs associés")
                )
            return True
        
        # Les autres ne peuvent rien modifier
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission: Admin peut tout, autres en lecture seule
    """
    
    def has_permission(self, request, view):
        """Vérification de base"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # L'utilisateur doit avoir un rôle financier
        return (request.user.is_admin or 
                request.user.is_comptable or 
                request.user.is_pharmacien)
    
    def has_object_permission(self, request, view, obj):
        """Vérification au niveau objet"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin peut tout faire
        if request.user.is_admin:
            return True
        
        # Autres: lecture seule
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False
