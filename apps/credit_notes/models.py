import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from apps.suppliers.models import Supplier


class CreditNote(models.Model):
    """
    Modèle pour les avoirs fournisseurs
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        verbose_name=_('Fournisseur')
    )

    invoice = models.ForeignKey(
        'invoices.Invoice',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='credit_notes',
        verbose_name=_('Facture associée')
    )
    
    credit_note_number = models.CharField(
        max_length=100,
        verbose_name=_('Numéro d\'avoir')
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Montant')
    )
    
    credit_note_date = models.DateField(
        verbose_name=_('Date d\'avoir')
    )

    motif = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Motif')
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
        db_table = 'credit_notes_credit_notes'
        verbose_name = _('Avoir')
        verbose_name_plural = _('Avoirs')
        ordering = ['-credit_note_date', '-created_at']
        indexes = [
            models.Index(fields=['supplier']),
            models.Index(fields=['credit_note_date']),
            models.Index(fields=['month', 'year']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.supplier.name} - {self.credit_note_number}"
    
    def save(self, *args, **kwargs):
        if self.credit_note_date:
            self.month = self.credit_note_date.month
            self.year = self.credit_note_date.year
        super().save(*args, **kwargs)
