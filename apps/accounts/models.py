import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec UUID et rôles pour la pharmacie
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        PHARMACIEN = 'PHARMACIEN', _('Pharmacien')
        COMPTABLE = 'COMPTABLE', _('Comptable')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COMPTABLE,
        verbose_name=_('Rôle')
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Téléphone')
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
        db_table = 'accounts_users'
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_pharmacien(self):
        return self.role == self.Role.PHARMACIEN
    
    @property
    def is_comptable(self):
        return self.role == self.Role.COMPTABLE


class ExpiringToken(models.Model):
    """
    Token with expiration for better security
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='auth_tokens'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'accounts_expiring_tokens'
        verbose_name = _('Token expirant')
        verbose_name_plural = _('Tokens expirants')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['key']),
        ]
    
    def __str__(self):
        return f"Token for {self.user.username}"
    
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        """Set expiration on save"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)
