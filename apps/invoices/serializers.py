from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Invoice
from apps.suppliers.serializers import SupplierSerializer


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les factures
    """
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_code = serializers.CharField(source='supplier.code', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'supplier', 'supplier_name', 'supplier_code',
            'invoice_number', 'net_to_pay',
            'invoice_date', 'due_date', 'status', 'notes', 'month', 'year', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'month', 'year', 'created_at', 'updated_at']
    
    def validate_invoice_number(self, value):
        """Validation du numéro de facture unique par fournisseur"""
        supplier = self.initial_data.get('supplier')
        if supplier:
            queryset = Invoice.objects.filter(
                supplier_id=supplier,
                invoice_number=value,
                is_active=True
            )
            
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "Une facture avec ce numéro existe déjà pour ce fournisseur"
                )
        return value
    
    def validate(self, attrs):
        """Validation des montants financiers"""
        net_to_pay = attrs.get('net_to_pay', Decimal('0.00'))
        
        # Validation que les montants sont positifs
        if net_to_pay < 0:
            raise serializers.ValidationError({
                'net_to_pay': "Le net à payer ne peut être négatif"
            })
        
        return attrs
    
    def validate_invoice_date(self, value):
        """Validation de la date de facture"""
        from django.utils import timezone
        from datetime import datetime
        
        # La date ne peut pas être dans le futur
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "La date de facture ne peut être dans le futur"
            )
        
        # La date ne peut pas être trop ancienne (plus de 2 ans)
        two_years_ago = timezone.now().date().replace(year=timezone.now().date().year - 2)
        if value < two_years_ago:
            raise serializers.ValidationError(
                "La date de facture ne peut être antérieure à 2 ans"
            )
        
        return value


class InvoiceListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des factures (allégé)
    """
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_code = serializers.CharField(source='supplier.code', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'supplier_name', 'supplier_code', 'invoice_number',
            'net_to_pay', 'invoice_date', 'due_date', 'status', 'notes', 
            'month', 'year', 'is_active', 'created_at'
        ]


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de factures
    """
    class Meta:
        model = Invoice
        fields = [
            'supplier', 'invoice_number', 'net_to_pay',
            'invoice_date', 'due_date', 'status', 'notes'
        ]
    
    def validate_invoice_number(self, value):
        """Validation du numéro de facture unique par fournisseur"""
        supplier = self.initial_data.get('supplier')
        if supplier:
            if Invoice.objects.filter(
                supplier_id=supplier,
                invoice_number=value,
                is_active=True
            ).exists():
                raise serializers.ValidationError(
                    "Une facture avec ce numéro existe déjà pour ce fournisseur"
                )
        return value


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des factures
    """
    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'net_to_pay',
            'invoice_date', 'due_date', 'status', 'notes'
        ]
        read_only_fields = ['id', 'month', 'year', 'created_at', 'updated_at', 'is_active']
    
    def validate_invoice_number(self, value):
        """Validation du numéro de facture unique par fournisseur"""
        supplier = self.initial_data.get('supplier') or (self.instance.supplier.id if self.instance.supplier else None)
        if supplier:
            queryset = Invoice.objects.filter(
                supplier_id=supplier,
                invoice_number=value,
                is_active=True
            )
            
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "Une facture avec ce numéro existe déjà pour ce fournisseur"
                )
        return value
