from rest_framework.permissions import BasePermission


class IsAuthenticatedOrCreateOnly(BasePermission):
    """
    Permission qui permet la création sans authentification
    mais nécessite l'authentification pour les autres actions
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user and request.user.is_authenticated
