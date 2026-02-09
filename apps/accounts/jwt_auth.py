"""
JWT Authentication with proper security
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework import status
from django.utils import timezone
import logging

logger = logging.getLogger('apps.authentication')

class CustomJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication with security hardening
    """
    
    def get_validated_token(self, raw_token):
        """Validate JWT with logging"""
        try:
            token = super().get_validated_token(raw_token)
            logger.info("JWT token validated successfully")
            return token
        except InvalidToken as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            raise AuthenticationFailed('Token invalide ou expiré')
    
    def get_user(self, validated_token):
        """Get user with security checks"""
        try:
            user = super().get_user(validated_token)
            
            if not user.is_active:
                logger.error(f"Inactive user attempted access: {user.id}")
                raise AuthenticationFailed('Utilisateur désactivé')
            
            # Log successful authentication
            logger.info(f"User authenticated: {user.id}")
            return user
            
        except Exception as e:
            logger.error(f"Error getting user from JWT: {str(e)}")
            raise AuthenticationFailed('Erreur d\'authentification')
