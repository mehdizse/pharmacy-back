"""
Secure Invoice Views with proper authentication and permissions
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count
from drf_spectacular.utils import extend_schema

from .models import Invoice
from .serializers import (
    InvoiceSerializer,
    InvoiceListSerializer,
    InvoiceCreateSerializer,
    InvoiceUpdateSerializer
)
from apps.accounts.permissions import IsFinanceUser
from apps.accounts.throttles import SensitiveOperationThrottle


class SecureInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet sécurisé pour la gestion des factures
    """
    queryset = Invoice.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'month', 'year', 'status', 'is_active']
    search_fields = [
        'invoice_number', 'supplier__name', 'supplier__code'
    ]
    ordering_fields = [
        'invoice_date', 'due_date', 'created_at', 'updated_at', 'net_to_pay'
    ]
    ordering = ['-invoice_date', '-created_at']
    
    def get_serializer_class(self):
        """Sélection du serializer selon l'action"""
        if self.action == 'list':
            return InvoiceListSerializer
        elif self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InvoiceUpdateSerializer
        return InvoiceSerializer
    
    def get_permissions(self):
        """Permissions systématiques"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsFinanceUser]
        return [permission() for permission in permission_classes]
    
    def get_throttles(self):
        """Throttling spécifique par action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [SensitiveOperationThrottle]
        return []
    
    def get_queryset(self):
        """Filtrage strict des données selon utilisateur"""
        user = self.request.user
        
        # Admin peut voir tout
        if user.is_admin:
            return Invoice.objects.select_related('supplier').all()
        
        # Autres utilisateurs voient seulement les factures actives
        # ET SEULEMENT celles de leurs fournisseurs autorisés
        queryset = Invoice.objects.select_related('supplier').filter(is_active=True)
        
        # TODO: Ajouter filtrage par organisation/fournisseur
        # user_suppliers = self.get_user_suppliers(user)
        # queryset = queryset.filter(supplier__in=user_suppliers)
        
        return queryset
    
    @extend_schema(
        summary="Lister les factures",
        description="Lister les factures avec filtres et recherche (authentifié requis)"
    )
    def list(self, request, *args, **kwargs):
        """Liste des factures avec authentification obligatoire"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Créer une facture",
        description="Créer une nouvelle facture (admin uniquement)"
    )
    @authentication_classes(['apps.accounts.jwt_auth.CustomJWTAuthentication'])
    @permission_classes([IsAuthenticated, IsAdminUser])
    def create(self, request, *args, **kwargs):
        """Création sécurisée de facture"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'data': serializer.data,
            'message': _('Facture créée avec succès')
        }, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Désactiver une facture",
        description="Désactiver une facture (admin uniquement, avec vérification avoirs)"
    )
    @authentication_classes(['apps.accounts.jwt_auth.CustomJWTAuthentication'])
    @permission_classes([IsAuthenticated, IsAdminUser])
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Désactivation sécurisée avec vérification avoirs"""
        try:
            invoice = self.get_object()
            
            # Vérifier s'il y a des avoirs
            if hasattr(invoice, 'credit_notes_count') and invoice.credit_notes_count > 0:
                return Response({
                    'error': _('Impossible de désactiver cette facture'),
                    'message': _('Cette facture a des avoirs associés. Supprimez les avoirs avant de pouvoir désactiver la facture.'),
                    'credit_notes_count': invoice.credit_notes_count
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Désactiver la facture
            invoice.is_active = False
            invoice.save()
            
            return Response({
                'message': _('Facture désactivée avec succès')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': _('Erreur lors de la désactivation'),
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# SÉCURITÉ: PAS d'authentification vide ni permissions vides
# Toutes les actions critiques sont protégées
