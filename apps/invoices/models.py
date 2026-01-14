import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from apps.suppliers.models import Supplier


class Invoice(models.Model):
    """
    Modèle pour les factures fournisseurs
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        verbose_name=_('Fournisseur')
    )
    
    invoice_number = models.CharField(
        max_length=100,
        verbose_name=_('Numéro de facture')
    )
    
    net_to_pay = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Net à payer')
    )
    
    invoice_date = models.DateField(
        verbose_name=_('Date de facture')
    )

    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Date d'échéance")
    )

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Brouillon')
        PENDING = 'PENDING', _('En attente')
        PAID = 'PAID', _('Payé')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_('Statut')
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    month = models.PositiveSmallIntegerField(
        verbose_name=_('Mois')
    )
    
    year = models.PositiveIntegerField(
        verbose_name=_('Année')
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
        db_table = 'invoices_invoices'
        verbose_name = _('Facture')
        verbose_name_plural = _('Factures')
        ordering = ['-invoice_date', '-created_at']
        unique_together = ['supplier', 'invoice_number']
        indexes = [
            models.Index(fields=['supplier']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['month', 'year']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.supplier.name} - {self.invoice_number}"
    
    def save(self, *args, **kwargs):
        if self.invoice_date:
            self.month = self.invoice_date.month
            self.year = self.invoice_date.year
        super().save(*args, **kwargs)
