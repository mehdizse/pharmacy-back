from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
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
from apps.accounts.permissions import IsFinanceUser, IsAdminUser
from .permissions import CanAccessInvoice, CanModifyInvoice


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des factures
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
    
    def get_permissions(self):
        """Gestion des permissions selon l'action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [CanModifyInvoice]
        else:
            permission_classes = [CanAccessInvoice]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrage des données selon l'utilisateur"""
        queryset = Invoice.objects.select_related('supplier').all()
        
        # Les non-admins ne voient que les factures actives
        if not self.request.user.is_admin:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @extend_schema(
        summary="Lister les factures",
        description="Lister toutes les factures avec filtres et recherche"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        """Sélection du serializer selon l'action"""
        if self.action == 'list':
            return InvoiceListSerializer
        elif self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InvoiceUpdateSerializer
        return InvoiceSerializer
    
    @extend_schema(
        summary="Créer une facture",
        description="Créer une nouvelle facture (Admin uniquement)"
    )
    @authentication_classes([])
    @permission_classes([])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        
        return Response(
            InvoiceSerializer(invoice).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Détails d'une facture",
        description="Obtenir les détails complets d'une facture"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Mettre à jour une facture",
        description="Mettre à jour les informations d'une facture (Admin uniquement)"
    )
    @authentication_classes([])
    @permission_classes([IsAdminUser])
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Vérifier si la facture a des avoirs associés (sauf pour les mises à jour mineures)
        if not partial:
            # Modification complète (PUT) - vérifier les avoirs
            from apps.credit_notes.models import CreditNote
            credit_notes_count = CreditNote.objects.filter(
                invoice=instance, 
                is_active=True
            ).count()
            
            if credit_notes_count > 0:
                return Response({
                    'error': 'Impossible de modifier cette facture',
                    'message': f'Cette facture a {credit_notes_count} avoir(s) associé(s). Veuillez supprimer les avoirs avant de modifier la facture.',
                    'credit_notes_count': credit_notes_count
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Modification partielle (PATCH) - autoriser certains champs
            restricted_fields = {'supplier', 'net_to_pay'}
            modified_fields = set(request.data.keys()) & restricted_fields
            
            if modified_fields:
                from apps.credit_notes.models import CreditNote
                credit_notes_count = CreditNote.objects.filter(
                    invoice=instance, 
                    is_active=True
                ).count()
                
                if credit_notes_count > 0:
                    return Response({
                        'error': 'Impossible de modifier ces champs',
                        'message': f'Les champs {", ".join(modified_fields)} ne peuvent pas être modifiés car cette facture a {credit_notes_count} avoir(s) associé(s).',
                        'restricted_fields': list(modified_fields),
                        'credit_notes_count': credit_notes_count
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        
        return Response(InvoiceSerializer(invoice).data)
    
    @extend_schema(
        summary="Supprimer une facture",
        description="Désactiver une facture (soft delete - Admin uniquement)"
    )
    @authentication_classes([])
    @permission_classes([IsAdminUser])
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Vérifier si la facture a des avoirs associés
        from apps.credit_notes.models import CreditNote
        credit_notes_count = CreditNote.objects.filter(
            invoice=instance, 
            is_active=True
        ).count()
        
        if credit_notes_count > 0:
            return Response({
                'error': 'Impossible de désactiver cette facture',
                'message': f'Cette facture a {credit_notes_count} avoir(s) associé(s). Veuillez supprimer les avoirs avant de désactiver la facture.',
                'credit_notes_count': credit_notes_count
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance.is_active = False
        instance.save()
        
        return Response({
            'message': 'Facture désactivée avec succès'
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Réactiver une facture",
        description="Réactiver une facture désactivée (Admin uniquement)"
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reactivate(self, request, pk=None):
        """Réactiver une facture"""
        invoice = self.get_object()
        invoice.is_active = True
        invoice.save()
        
        return Response({
            'message': 'Facture réactivée avec succès'
        })
    
    @extend_schema(
        summary="Lister les avoirs d'une facture",
        description="Obtenir la liste des avoirs associés à cette facture"
    )
    @action(detail=True, methods=['get'], permission_classes=[IsFinanceUser])
    def credit_notes(self, request, pk=None):
        """Lister les avoirs associés à cette facture"""
        invoice = self.get_object()
        from apps.credit_notes.models import CreditNote
        from apps.credit_notes.serializers import CreditNoteListSerializer
        
        credit_notes = CreditNote.objects.filter(
            invoice=invoice,
            is_active=True
        ).select_related('supplier').order_by('-created_at')
        
        serializer = CreditNoteListSerializer(credit_notes, many=True)
        
        return Response({
            'invoice': {
                'id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'supplier_name': invoice.supplier.name
            },
            'credit_notes': serializer.data,
            'count': credit_notes.count()
        })
    
    @extend_schema(
        summary="Statistiques par fournisseur",
        description="Obtenir les statistiques des factures par fournisseur"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsFinanceUser])
    def by_supplier(self, request):
        """Statistiques des factures par fournisseur"""
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
            total_invoices=Sum('net_to_pay'),
            invoice_count=Count('id')
        ).order_by('-total_invoices')
        
        return Response({
            'period': {'month': month, 'year': year} if month or year else None,
            'statistics': list(stats)
        })
    
    @extend_schema(
        summary="Total mensuel",
        description="Calculer le total mensuel des factures"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsFinanceUser])
    def monthly_total(self, request):
        """Calculer le total mensuel des factures"""
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
            total_invoices=Sum('net_to_pay'),
            invoice_count=Count('id')
        )
        
        return Response({
            'period': {'month': month, 'year': year},
            'totals': totals
        })
