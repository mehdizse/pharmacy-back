"""
Middleware hybride pour gérer Django Token et JWT
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.authtoken.models import Token
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class HybridTokenAuthentication:
    """
    Middleware d'authentification hybride qui gère Django Token et JWT
    """
    
    def authenticate(self, request):
        """
        Tente d'authentifier avec JWT ou Django Token
        """
        auth_header = self.get_authorization_header(request)
        
        if not auth_header:
            return None
            
        try:
            # Essaie d'abord avec JWT
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                jwt_auth = JWTAuthentication()
                return jwt_auth.authenticate(request)
            else:
                # Essaie avec Django Token
                token_key = auth_header
                token = Token.objects.get(key=token_key)
                if token and token.user.is_active:
                    return token.user
                return None
                
        except InvalidToken:
            logger.warning("JWT token invalide")
        except Exception as e:
            logger.error(f"Erreur d'authentification: {str(e)}")
            
        return None
    
    def get_authorization_header(self, request):
        """Extrait le header Authorization"""
        auth = request.META.get('HTTP_AUTHORIZATION')
        if auth and auth.startswith('Token '):
            return auth
        elif auth and auth.startswith('Bearer '):
            return auth
        return None
