from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CreditNote


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    """Configuration admin pour le modèle CreditNote"""
    
    list_display = [
        'credit_note_number', 'supplier', 'credit_note_date',
        'amount', 'is_active', 'created_at'
    ]
    list_filter = [
        'supplier', 'month', 'year', 'is_active',
        'created_at', 'credit_note_date'
    ]
    search_fields = [
        'credit_note_number', 'supplier__name', 'supplier__code'
    ]
    ordering = ['-credit_note_date', '-created_at']
    
    readonly_fields = ['month', 'year', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': (
                'supplier', 'credit_note_number', 'credit_note_date'
            )
        }),
        (_('Motif'), {
            'fields': (
                'motif',
            )
        }),
        (_('Montant'), {
            'fields': (
                'amount',
            )
        }),
        (_('Période'), {
            'fields': (
                'month', 'year'
            ),
            'classes': ('collapse',)
        }),
        (_('Audit'), {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Rendre certains champs readonly en modification"""
        if obj:  # Modification
            return self.readonly_fields + ['supplier']
        return self.readonly_fields
