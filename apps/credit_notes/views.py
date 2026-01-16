from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count
from drf_spectacular.utils import extend_schema

from .models import CreditNote
from .serializers import (
    CreditNoteSerializer,
    CreditNoteListSerializer,
    CreditNoteCreateSerializer,
    CreditNoteUpdateSerializer
)
from apps.accounts.permissions import IsFinanceUser, IsAdminUser


class CreditNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des avoirs
    """
    queryset = CreditNote.objects.select_related('supplier', 'invoice').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'month', 'year']
    search_fields = [
        'credit_note_number', 'supplier__name', 'supplier__code', 'motif'
    ]
    ordering_fields = [
        'credit_note_date', 'created_at', 'updated_at', 'amount'
    ]
    ordering = ['-credit_note_date', '-created_at']
    
    def get_serializer_class(self):
        """Sélection du serializer selon l'action"""
        if self.action == 'list':
            return CreditNoteListSerializer
        elif self.action == 'create':
            return CreditNoteCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CreditNoteUpdateSerializer
        return CreditNoteSerializer
    
    def get_permissions(self):
        """Gestion des permissions selon l'action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsFinanceUser]
        return [permission() for permission in permission_classes]
    
    @extend_schema(
        summary="Lister les avoirs",
        description="Lister tous les avoirs avec filtres et recherche"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Créer un avoir",
        description="Créer un nouvel avoir (Admin uniquement)"
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credit_note = serializer.save()
        
        return Response(
            CreditNoteSerializer(credit_note).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Détails d'un avoir",
        description="Obtenir les détails complets d'un avoir"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Mettre à jour un avoir",
        description="Mettre à jour les informations d'un avoir (Admin uniquement)"
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        credit_note = serializer.save()
        
        return Response(CreditNoteSerializer(credit_note).data)
    
    @extend_schema(
        summary="Supprimer un avoir",
        description="Supprimer définitivement un avoir (Admin uniquement)"
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        credit_note_number = instance.credit_note_number
        supplier_name = instance.supplier.name
        
        # Suppression définitive
        instance.delete()
        
        return Response({
            'message': _('Avoir "{}" du fournisseur "{}" supprimé définitivement').format(credit_note_number, supplier_name)
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Statistiques par fournisseur",
        description="Obtenir les statistiques des avoirs par fournisseur"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsFinanceUser])
    def by_supplier(self, request):
        """Statistiques des avoirs par fournisseur"""
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        queryset = self.queryset
        
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        stats = queryset.values(
            'supplier__id',
            'supplier__name',
            'supplier__code'
        ).annotate(
            total_credit_notes=Sum('amount'),
            credit_note_count=Count('id')
        ).order_by('-total_credit_notes')
        
        return Response({
            'period': {'month': month, 'year': year} if month or year else None,
            'statistics': list(stats)
        })
    
    @extend_schema(
        summary="Total mensuel",
        description="Calculer le total mensuel des avoirs"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsFinanceUser])
    def monthly_total(self, request):
        """Calculer le total mensuel des avoirs"""
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not month or not year:
            return Response({
                'error': _('Les paramètres month et year sont obligatoires')
            }, status=400)
        
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({
                'error': _('Paramètres month et year invalides')
            }, status=400)
        
        queryset = self.queryset.filter(
            month=month,
            year=year
        )
        
        totals = queryset.aggregate(
            total_credit_notes=Sum('amount'),
            credit_note_count=Count('id')
        )
        
        return Response({
            'period': {'month': month, 'year': year},
            'totals': totals
        })
