from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema

from .models import Supplier
from .serializers import (
    SupplierSerializer,
    SupplierListSerializer,
    SupplierCreateSerializer,
    SupplierUpdateSerializer
)
from apps.accounts.permissions import IsFinanceUser, IsAdminUser


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des fournisseurs
    """
    queryset = Supplier.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'city']
    search_fields = ['name', 'code', 'email', 'siret']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Sélection du serializer selon l'action"""
        if self.action == 'list':
            return SupplierListSerializer
        elif self.action == 'create':
            return SupplierCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SupplierUpdateSerializer
        return SupplierSerializer
    
    def get_permissions(self):
        """Gestion des permissions selon l'action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsFinanceUser]
        return [permission() for permission in permission_classes]
    
    @extend_schema(
        summary="Lister les fournisseurs",
        description="Lister tous les fournisseurs avec filtres et recherche"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Créer un fournisseur",
        description="Créer un nouveau fournisseur (Admin uniquement)"
    )
    @authentication_classes([])
    @permission_classes([])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        supplier = serializer.save()
        
        return Response(
            SupplierSerializer(supplier).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Détails d'un fournisseur",
        description="Obtenir les détails complets d'un fournisseur"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Mettre à jour un fournisseur",
        description="Mettre à jour les informations d'un fournisseur (Admin uniquement)"
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        supplier = serializer.save()
        
        return Response(SupplierSerializer(supplier).data)
    
    @extend_schema(
        summary="Supprimer un fournisseur",
        description="Désactiver un fournisseur (soft delete - Admin uniquement)"
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response({
            'message': _('Fournisseur désactivé avec succès')
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Réactiver un fournisseur",
        description="Réactiver un fournisseur désactivé (Admin uniquement)"
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reactivate(self, request, pk=None):
        """Réactiver un fournisseur"""
        supplier = self.get_object()
        supplier.is_active = True
        supplier.save()
        
        return Response({
            'message': _('Fournisseur réactivé avec succès')
        })
    
    @extend_schema(
        summary="Statistiques fournisseur",
        description="Obtenir les statistiques détaillées d'un fournisseur"
    )
    @action(detail=True, methods=['get'], permission_classes=[IsFinanceUser])
    def statistics(self, request, pk=None):
        """Obtenir les statistiques d'un fournisseur"""
        supplier = self.get_object()
        
        return Response({
            'supplier': SupplierSerializer(supplier).data,
            'invoice_count': supplier.get_invoice_count(),
            'credit_note_count': supplier.get_credit_note_count(),
            'total_invoices_amount': supplier.get_total_invoices_amount(),
            'total_credit_notes_amount': supplier.get_total_credit_notes_amount(),
            'net_amount': (
                supplier.get_total_invoices_amount() - 
                supplier.get_total_credit_notes_amount()
            )
        })
    
    @extend_schema(
        summary="Fournisseurs actifs",
        description="Lister uniquement les fournisseurs actifs"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsFinanceUser])
    def active(self, request):
        """Lister les fournisseurs actifs"""
        queryset = self.queryset.filter(is_active=True)
        serializer = SupplierListSerializer(queryset, many=True)
        return Response(serializer.data)
