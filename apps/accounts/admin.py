from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuration admin pour le modèle User"""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'role', 'is_active', 'date_joined'
    ]
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser',
        'date_joined'
    ]
    search_fields = [
        'username', 'email', 'first_name', 'last_name'
    ]
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Informations personnelles'), {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        (_('Rôle et permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Dates importantes'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined', 'created_at', 'updated_at']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2', 'role', 'phone'
            ),
        }),
    )
