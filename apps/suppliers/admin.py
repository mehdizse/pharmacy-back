from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Configuration admin pour le modèle Supplier"""
    
    list_display = [
        'name', 'code', 'city', 'phone', 'email',
        'is_active', 'payment_terms', 'created_at'
    ]
    list_filter = [
        'is_active', 'city', 'payment_terms', 'created_at'
    ]
    search_fields = [
        'name', 'code', 'email', 'siret', 'contact_person'
    ]
    ordering = ['name']
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': (
                'name', 'code', 'siret', 'contact_person', 'payment_terms'
            )
        }),
        (_('Adresse'), {
            'fields': (
                'address', 'postal_code', 'city'
            ),
            'classes': ('collapse',)
        }),
        (_('Contact'), {
            'fields': (
                'phone', 'email'
            )
        }),
        (_('Statut'), {
            'fields': (
                'is_active',
            )
        }),
        (_('Audit'), {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        """Rendre certains champs readonly en modification"""
        if obj:  # Modification
            return self.readonly_fields + ['code', 'siret']
        return self.readonly_fields
