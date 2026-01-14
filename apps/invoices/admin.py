from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Configuration admin pour le modèle Invoice"""
    
    list_display = [
        'invoice_number', 'supplier', 'invoice_date', 'due_date',
        'net_to_pay', 'status', 'is_active', 'created_at'
    ]
    list_filter = [
        'supplier', 'month', 'year', 'status', 'is_active',
        'created_at', 'invoice_date'
    ]
    search_fields = [
        'invoice_number', 'supplier__name', 'supplier__code'
    ]
    ordering = ['-invoice_date', '-created_at']
    
    readonly_fields = ['month', 'year', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': (
                'supplier', 'invoice_number', 'invoice_date', 'due_date'
            )
        }),
        (_('Montants financiers'), {
            'fields': (
                'net_to_pay',
            )
        }),
        (_('Période'), {
            'fields': (
                'month', 'year'
            ),
            'classes': ('collapse',)
        }),
        (_('Statut'), {
            'fields': (
                'status', 'is_active',
            )
        }),
        (_('Notes'), {
            'fields': (
                'notes',
            )
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
