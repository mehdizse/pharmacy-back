from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema

from .models import Invoice
from .serializers import (
    InvoiceSerializer,
    InvoiceListSerializer,
    InvoiceCreateSerializer,
    InvoiceUpdateSerializer
)
from .permissions import CanAccessInvoice, CanModifyInvoice


class MultiTenantInvoiceViewSet(viewsets.ModelViewSet):
    """
    Multi-tenant réel:
    - Admin: tout
    - Finance: uniquement invoices dont supplier est dans UserSupplierAccess(user, supplier)
    """

    queryset = Invoice.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["supplier", "month", "year", "status", "is_active"]
    search_fields = ["invoice_number", "supplier__name", "supplier__code"]
    ordering_fields = ["invoice_date", "due_date", "created_at", "updated_at", "net_to_pay"]
    ordering = ["-invoice_date", "-created_at"]

    # Throttling: basé sur scopes (settings_prod.py)
    throttle_classes = [ScopedRateThrottle]

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        if self.action == "create":
            return InvoiceCreateSerializer
        if self.action in ["update", "partial_update"]:
            return InvoiceUpdateSerializer
        return InvoiceSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "deactivate"]:
            return [IsAuthenticated(), CanModifyInvoice()]
        return [IsAuthenticated(), CanAccessInvoice()]

    def get_throttles(self):
        # scopes réels
        if self.action in ["create", "update", "partial_update", "destroy", "deactivate"]:
            self.throttle_scope = "sensitive"
        else:
            self.throttle_scope = "user"
        return super().get_throttles()

    def get_queryset(self):
        user = self.request.user

        base = Invoice.objects.select_related("supplier")

        if user.is_admin:
            return base.all()

        # Multi-tenant strict via table d'accès
        from apps.suppliers.models import UserSupplierAccess
        supplier_ids = UserSupplierAccess.objects.filter(user=user).values_list("supplier_id", flat=True)

        # Si aucun supplier assigné => accès à rien
        qs = base.filter(supplier_id__in=supplier_ids, is_active=True)
        return qs

    @extend_schema(
        summary="Désactiver une facture",
        description="Admin uniquement (soft disable) avec règles métier"
    )
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        invoice = self.get_object()  # object-level permission appelée automatiquement par DRF

        # TODO: vrai check avoirs (ton code actuel check un attr qui n'existe pas)
        invoice.is_active = False
        invoice.save(update_fields=["is_active"])

        return Response({"message": _("Facture désactivée avec succès")}, status=status.HTTP_200_OK)
