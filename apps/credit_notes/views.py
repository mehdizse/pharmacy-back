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
    queryset = CreditNote.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'month', 'year', 'status', 'is_active']
    search_fields = [
        'credit_note_number', 'supplier__name', 'supplier__code', 'motif'
    ]
    ordering_fields = [
        'credit_note_date', 'created_at', 'updated_at', 'amount', 'status'
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
    
    def get_queryset(self):
        """Optimisation des requêtes avec select_related"""
        return CreditNote.objects.select_related('supplier', 'invoice').all()
    
    @extend_schema(
        summary="Lister les avoirs",
        description="Lister tous les avoirs avec filtres et recherche"
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
        description="Désactiver un avoir (soft delete - Admin uniquement)"
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response({
            'message': _('Avoir désactivé avec succès')
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Réactiver un avoir",
        description="Réactiver un avoir désactivé (Admin uniquement)"
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reactivate(self, request, pk=None):
        """Réactiver un avoir"""
        credit_note = self.get_object()
        credit_note.is_active = True
        credit_note.save()
        
        return Response({
            'message': _('Avoir réactivé avec succès')
        })
    
    @extend_schema(
        summary="Statistiques par fournisseur",
        description="Obtenir les statistiques des avoirs par fournisseur"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsFinanceUser])
    def by_supplier(self, request):
        """Statistiques des avoirs par fournisseur"""
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        queryset = self.get_queryset().filter(is_active=True)
        
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
        
        queryset = self.get_queryset().filter(
            month=month,
            year=year,
            is_active=True
        )
        
        totals = queryset.aggregate(
            total_credit_notes=Sum('amount'),
            credit_note_count=Count('id')
        )
        
        return Response({
            'period': {'month': month, 'year': year},
            'totals': totals
        })
