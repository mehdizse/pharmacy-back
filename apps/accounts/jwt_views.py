"""
JWT Views with proper security
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils.translation import gettext_lazy as _
import logging

from .serializers import UserLoginSerializer
from .models import User

logger = logging.getLogger("apps.authentication")


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    JWT Login with security logging
    """
    serializer_class = UserLoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = serializer.validated_data['user']
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Log successful login
            logger.info(f"User login successful: {user.username}")
            
            resp = Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_admin': user.is_admin,
                    'is_pharmacien': user.is_pharmacien,
                    'is_comptable': user.is_comptable,
                },
                'message': _('Connexion réussie')
            }, status=status.HTTP_200_OK)
            
            return resp
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({
                'error': _('Erreur de connexion')
            }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "refresh"


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def jwt_logout_view(request):
    """
    Logout stateless correct:
    - blacklist le refresh token
    - NE PRÉTEND PAS invalider l'access token (reste valide jusqu'à exp)
    """
    # scope logout => tu peux réutiliser "refresh" ou créer "logout"
    request.throttle_scope = "refresh"

    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"error": _("Refresh token requis")}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": _("Déconnexion réussie")}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.warning(f"Logout failed: {e}")
        return Response({"error": _("Token invalide ou expiré")}, status=status.HTTP_401_UNAUTHORIZED)
