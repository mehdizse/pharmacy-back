from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserListSerializer
)
from .permissions import IsAdminUser, IsFinanceUser
from .throttles import LoginRateThrottle


class UserRegistrationView(generics.CreateAPIView):
    """
    Inscription d'un nouvel utilisateur
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        summary="Inscrire un nouvel utilisateur",
        description="Créer un nouveau compte utilisateur (Admin uniquement)",
        responses={201: UserProfileSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Créer un token pour le nouvel utilisateur
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': _('Utilisateur créé avec succès')
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    Connexion d'un utilisateur
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginRateThrottle]
    
    @extend_schema(
        summary="Connexion utilisateur",
        description="Authentifier un utilisateur et retourner un token",
        responses={200: UserProfileSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Créer ou récupérer le token
        token, created = Token.objects.get_or_create(user=user)
        
        # Connexion de l'utilisateur
        login(request, user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': _('Connexion réussie')
        })


class UserLogoutView(generics.GenericAPIView):
    """
    Déconnexion d'un utilisateur
    """
    serializer_class = UserProfileSerializer  # Ajout du serializer_class
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Déconnexion utilisateur",
        description="Déconnecter l'utilisateur et supprimer le token",
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request, *args, **kwargs):
        try:
            # Supprimer le token
            request.user.auth_token.delete()
        except:
            pass
        
        # Déconnexion
        logout(request)
        
        return Response({
            'message': _('Déconnexion réussie')
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Afficher et modifier le profil utilisateur
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Obtenir le profil utilisateur",
        description="Récupérer les informations du profil utilisateur connecté"
    )
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Mettre à jour le profil utilisateur",
        description="Mettre à jour les informations du profil utilisateur"
    )
    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'user': serializer.data,
            'message': _('Profil mis à jour avec succès')
        })


class UserListView(generics.ListAPIView):
    """
    Lister tous les utilisateurs (admin seulement)
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        summary="Lister tous les utilisateurs",
        description="Lister tous les utilisateurs du système (Admin uniquement)"
    )
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsFinanceUser])
@extend_schema(
    summary="Vérifier l'authentification",
    description="Vérifier si l'utilisateur est authentifié et a accès aux données financières",
    tags=["Authentication"]
)
def check_auth(request):
    """
    Vérifier l'authentification et les permissions
    """
    return Response({
        'authenticated': True,
        'user': {
            'id': str(request.user.id),
            'username': request.user.username,
            'role': request.user.role,
            'role_display': request.user.get_role_display()
        },
        'permissions': {
            'is_admin': request.user.is_admin,
            'is_pharmacien': request.user.is_pharmacien,
            'is_comptable': request.user.is_comptable,
            'can_access_finance': (
                request.user.is_comptable or 
                request.user.is_pharmacien or 
                request.user.is_admin
            )
        }
    })
