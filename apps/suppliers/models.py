import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class UserSupplierAccess(models.Model):
    """
    Table d'association utilisateur → fournisseurs (multi-tenant)
    """
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='supplier_access',
        verbose_name=_('Utilisateur')
    )
    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='user_access',
        verbose_name=_('Fournisseur')
    )
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Accordé le'))
    granted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_access',
        verbose_name=_('Accordé par')
    )
    
    class Meta:
        db_table = 'suppliers_user_access'
        unique_together = ['user', 'supplier']
        verbose_name = _('Accès fournisseur')
        verbose_name_plural = _('Accès fournisseurs')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['supplier']),
        ]
    
    def __str__(self):
        return f"{self.user.username} → {self.supplier.name}"


class Supplier(models.Model):
    """
    Fournisseur avec support multi-tenant
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name=_('Nom du fournisseur')
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]{3,20}$',
                message=_('Le code doit contenir uniquement des majuscules et chiffres (3-20 caractères)')
            )
        ],
        verbose_name=_('Code fournisseur')
    )
    
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Téléphone'))
    siret = models.CharField(max_length=14, blank=True, null=True, verbose_name=_('SIRET'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Adresse'))
    is_active = models.BooleanField(default=True, verbose_name=_('Actif'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Mis à jour le'))
    
    class Meta:
        db_table = 'suppliers_suppliers'
        verbose_name = _('Fournisseur')
        verbose_name_plural = _('Fournisseurs')
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    # Propriétés calculées
    @property
    def full_address(self):
        """Adresse complète"""
        if self.address:
            return self.address.strip()
        return ""
    
    @property
    def invoice_count(self):
        """Nombre de factures"""
        from apps.invoices.models import Invoice
        return Invoice.objects.filter(supplier=self, is_active=True).count()
    
    @property
    def credit_note_count(self):
        """Nombre d'avoirs"""
        from apps.credit_notes.models import CreditNote
        return CreditNote.objects.filter(invoice__supplier=self, invoice__is_active=True).count()
    
    @property
    def total_invoices_amount(self):
        """Montant total des factures"""
        from apps.invoices.models import Invoice
        return Invoice.objects.filter(supplier=self, is_active=True).aggregate(
            total=models.Sum('net_to_pay')
        )['total'] or 0
    
    @property
    def total_credit_notes_amount(self):
        """Montant total des avoirs"""
        from apps.credit_notes.models import CreditNote
        return CreditNote.objects.filter(invoice__supplier=self, invoice__is_active=True).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Adresse')
    )
    
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{5}$',
                message=_('Le code postal doit contenir 5 chiffres')
            )
        ],
        verbose_name=_('Code postal')
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Ville')
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9+\s()-]{10,20}$',
                message=_('Format de téléphone invalide')
            )
        ],
        verbose_name=_('Téléphone')
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email')
    )
    
    siret = models.CharField(
        max_length=14,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{14}$',
                message=_('Le SIRET doit contenir 14 chiffres')
            )
        ],
        verbose_name=_('SIRET')
    )
    
    contact_person = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Personne de contact')
    )
    
    payment_terms = models.IntegerField(
        default=30,
        blank=True,
        null=True,
        verbose_name=_('Délai de paiement (jours)')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Actif')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Créé le')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Mis à jour le')
    )
    
    class Meta:
        db_table = 'suppliers_suppliers'
        verbose_name = _('Fournisseur')
        verbose_name_plural = _('Fournisseurs')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['siret']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else f"{self.name}"
    
    @extend_schema_field(OpenApiTypes.STR)
    def full_address(self):
        """Retourne l'adresse complète formatée"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.postal_code and self.city:
            parts.append(f"{self.postal_code} {self.city}")
        return " - ".join(parts) if parts else _("Non spécifiée")
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_invoice_count(self):
        """Retourne le nombre de factures pour ce fournisseur"""
        from apps.invoices.models import Invoice
        return Invoice.objects.filter(supplier=self, is_active=True).count()
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_credit_note_count(self):
        """Retourne le nombre d'avoirs pour ce fournisseur"""
        from apps.credit_notes.models import CreditNote
        return CreditNote.objects.filter(supplier=self, is_active=True).count()
    
    @extend_schema_field(OpenApiTypes.DECIMAL)
    def get_total_invoices_amount(self):
        """Retourne le montant total des factures"""
        from apps.invoices.models import Invoice
        from django.db.models import Sum
        
        result = Invoice.objects.filter(
            supplier=self, 
            is_active=True
        ).aggregate(total=Sum('net_to_pay'))
        
        return result['total'] or 0
    
    @extend_schema_field(OpenApiTypes.DECIMAL)
    def get_total_credit_notes_amount(self):
        """Retourne le montant total des avoirs"""
        from apps.credit_notes.models import CreditNote
        from django.db.models import Sum
        
        result = CreditNote.objects.filter(
            supplier=self, 
            is_active=True
        ).aggregate(total=Sum('amount'))
        
        return result['total'] or 0
