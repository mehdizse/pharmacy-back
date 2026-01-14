from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les fournisseurs
    """
    full_address = serializers.ReadOnlyField()
    invoice_count = serializers.ReadOnlyField()
    credit_note_count = serializers.ReadOnlyField()
    total_invoices_amount = serializers.ReadOnlyField()
    total_credit_notes_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'code', 'address', 'postal_code', 'city',
            'phone', 'email', 'siret', 'contact_person', 'payment_terms',
            'is_active', 'created_at', 'updated_at',
            'full_address', 'invoice_count', 'credit_note_count',
            'total_invoices_amount', 'total_credit_notes_amount'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validation du nom du fournisseur"""
        if Supplier.objects.filter(name__iexact=value).exists():
            if self.instance and self.instance.name.lower() != value.lower():
                raise serializers.ValidationError(
                    _("Un fournisseur avec ce nom existe déjà")
                )
        return value
    
    def validate_code(self, value):
        """Validation du code fournisseur"""
        if value in (None, ''):
            return None
        if Supplier.objects.filter(code__iexact=value).exists():
            if self.instance and self.instance.code.lower() != value.lower():
                raise serializers.ValidationError(
                    _("Un fournisseur avec ce code existe déjà")
                )
        return value.upper()
    
    def validate_siret(self, value):
        """Validation du SIRET"""
        if value in (None, ''):
            return None
        if Supplier.objects.filter(siret=value).exists():
            if self.instance and self.instance.siret != value:
                raise serializers.ValidationError(
                    _("Un fournisseur avec ce SIRET existe déjà")
                )
        return value
    
    def validate_payment_terms(self, value):
        """Validation des conditions de paiement"""
        if value is None:
            return None
        if value <= 0:
            raise serializers.ValidationError(
                _("Le délai de paiement doit être positif")
            )
        if value > 365:
            raise serializers.ValidationError(
                _("Le délai de paiement ne peut dépasser 365 jours")
            )
        return value


class SupplierListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des fournisseurs (allégé)
    """
    invoice_count = serializers.ReadOnlyField()
    total_invoices_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'code', 'city', 'phone', 'email',
            'is_active', 'invoice_count', 'total_invoices_amount'
        ]


class SupplierCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de fournisseurs
    """
    code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    siret = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Supplier
        fields = [
            'name', 'code', 'address', 'postal_code', 'city',
            'phone', 'email', 'siret', 'contact_person', 'payment_terms'
        ]
        extra_kwargs = {
            'code': {'required': False, 'allow_null': True, 'allow_blank': True},
            'address': {'required': False, 'allow_null': True, 'allow_blank': True},
            'postal_code': {'required': False, 'allow_null': True, 'allow_blank': True},
            'city': {'required': False, 'allow_null': True, 'allow_blank': True},
            'phone': {'required': False, 'allow_null': True, 'allow_blank': True},
            'email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'siret': {'required': False, 'allow_null': True, 'allow_blank': True},
            'contact_person': {'required': False, 'allow_null': True, 'allow_blank': True},
            'payment_terms': {'required': False, 'allow_null': True},
        }
    
    def validate_code(self, value):
        """Validation du code fournisseur"""
        if value in (None, ''):
            return None
        if Supplier.objects.filter(code__iexact=value).exists():
            raise serializers.ValidationError(
                _("Un fournisseur avec ce code existe déjà")
            )
        return value.upper()

    def validate_siret(self, value):
        """Validation du SIRET"""
        if value in (None, ''):
            return None
        if Supplier.objects.filter(siret=value).exists():
            raise serializers.ValidationError(
                _("Un fournisseur avec ce SIRET existe déjà")
            )
        return value


class SupplierUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des fournisseurs
    """
    class Meta:
        model = Supplier
        fields = [
            'name', 'address', 'postal_code', 'city',
            'phone', 'email', 'contact_person', 'payment_terms', 'is_active'
        ]
        extra_kwargs = {
            'name': {'required': False},
            'address': {'required': False, 'allow_null': True, 'allow_blank': True},
            'postal_code': {'required': False, 'allow_null': True, 'allow_blank': True},
            'city': {'required': False, 'allow_null': True, 'allow_blank': True},
            'phone': {'required': False, 'allow_null': True, 'allow_blank': True},
            'email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'contact_person': {'required': False, 'allow_null': True, 'allow_blank': True},
            'payment_terms': {'required': False, 'allow_null': True},
            'is_active': {'required': False},
        }
    
    def validate_name(self, value):
        """Validation du nom du fournisseur"""
        if Supplier.objects.filter(name__iexact=value).exists():
            if self.instance and self.instance.name.lower() != value.lower():
                raise serializers.ValidationError(
                    _("Un fournisseur avec ce nom existe déjà")
                )
        return value
