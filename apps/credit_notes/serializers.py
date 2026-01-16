from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from .models import CreditNote
from apps.suppliers.serializers import SupplierSerializer
from apps.invoices.models import Invoice


class CreditNoteSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les avoirs
    """
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_code = serializers.CharField(source='supplier.code', read_only=True)
    invoice_id = serializers.UUIDField(source='invoice.id', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    
    class Meta:
        model = CreditNote
        fields = [
            'id', 'supplier', 'supplier_name', 'supplier_code',
            'invoice', 'invoice_id', 'invoice_number',
            'credit_note_number', 'amount', 'credit_note_date', 'motif',
            'month', 'year', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'month', 'year', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        """Validation du montant de l'avoir"""
        if value <= 0:
            raise serializers.ValidationError(
                _("Le montant de l'avoir doit être positif")
            )
        
        # Validation du montant maximum (ex: 1 million d'euros)
        if value > Decimal('1000000.00'):
            raise serializers.ValidationError(
                _("Le montant de l'avoir ne peut dépasser 1 000 000,00 €")
            )
        
        return value
    
    def validate_credit_note_number(self, value):
        """Validation du numéro d'avoir unique par fournisseur"""
        supplier = self.initial_data.get('supplier')
        if supplier:
            queryset = CreditNote.objects.filter(
                supplier_id=supplier,
                credit_note_number=value,
                is_active=True
            )
            
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    _("Un avoir avec ce numéro existe déjà pour ce fournisseur")
                )
        return value
    
    def validate_credit_note_date(self, value):
        """Validation de la date d'avoir"""
        from django.utils import timezone
        
        # La date ne peut pas être dans le futur
        if value > timezone.now().date():
            raise serializers.ValidationError(
                _("La date d'avoir ne peut être dans le futur")
            )
        
        # La date ne peut pas être trop ancienne (plus de 2 ans)
        two_years_ago = timezone.now().date().replace(year=timezone.now().date().year - 2)
        if value < two_years_ago:
            raise serializers.ValidationError(
                _("La date d'avoir ne peut être antérieure à 2 ans")
            )
        
        return value


class CreditNoteListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des avoirs (allégé)
    """
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_code = serializers.CharField(source='supplier.code', read_only=True)
    invoice_id = serializers.UUIDField(source='invoice.id', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    
    class Meta:
        model = CreditNote
        fields = [
            'id', 'supplier_name', 'supplier_code', 'credit_note_number',
            'invoice_id', 'invoice_number',
            'amount', 'credit_note_date', 'motif', 'month', 'year', 'is_active'
        ]


class CreditNoteCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'avoirs
    """
    reason = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CreditNote
        fields = [
            'invoice', 'supplier', 'credit_note_number', 'amount', 'credit_note_date', 'motif', 'reason'
        ]

    def validate(self, attrs):
        invoice = attrs.get('invoice')
        supplier = attrs.get('supplier')
        reason = attrs.get('reason')

        if not attrs.get('motif') and reason:
            attrs['motif'] = reason

        attrs.pop('reason', None)

        if invoice and not supplier:
            attrs['supplier'] = invoice.supplier

        if supplier and invoice and invoice.supplier_id != supplier.id:
            raise serializers.ValidationError({
                'invoice': _("La facture sélectionnée n'appartient pas au fournisseur indiqué")
            })

        if not attrs.get('supplier') and not invoice:
            raise serializers.ValidationError({
                'supplier': _("Ce champ est obligatoire.")
            })

        return attrs
    
    def validate_credit_note_number(self, value):
        """Validation du numéro d'avoir unique par fournisseur"""
        supplier_id = self.initial_data.get('supplier')
        if not supplier_id:
            invoice_id = self.initial_data.get('invoice')
            if invoice_id:
                try:
                    supplier_id = Invoice.objects.only('supplier_id').get(id=invoice_id).supplier_id
                except Invoice.DoesNotExist:
                    supplier_id = None

        if supplier_id:
            if CreditNote.objects.filter(
                supplier_id=supplier_id,
                credit_note_number=value,
                is_active=True
            ).exists():
                raise serializers.ValidationError(
                    _("Un avoir avec ce numéro existe déjà pour ce fournisseur")
                )
        return value


class CreditNoteUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des avoirs
    """
    reason = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CreditNote
        fields = [
            'invoice', 'credit_note_number', 'amount', 'credit_note_date', 'motif', 'reason', 'is_active'
        ]

    def validate(self, attrs):
        reason = attrs.get('reason')

        if not attrs.get('motif') and reason:
            attrs['motif'] = reason

        attrs.pop('reason', None)

        return attrs
    
    def validate_credit_note_number(self, value):
        """Validation du numéro d'avoir unique par fournisseur"""
        if self.instance and self.instance.supplier:
            queryset = CreditNote.objects.filter(
                supplier=self.instance.supplier,
                credit_note_number=value,
                is_active=True
            ).exclude(id=self.instance.id)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    _("Un avoir avec ce numéro existe déjà pour ce fournisseur")
                )
        return value
