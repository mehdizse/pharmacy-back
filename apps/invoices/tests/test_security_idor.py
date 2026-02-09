from rest_framework.test import APITestCase
from django.urls import reverse

from apps.suppliers.models import Supplier, UserSupplierAccess
from apps.accounts.models import User
from apps.invoices.models import Invoice


class TestInvoiceIDOR(APITestCase):
    def setUp(self):
        # Users
        self.admin = User.objects.create_user(username="admin", password="pass", role="admin")
        self.admin.is_admin = True
        self.admin.save()

        self.user_a = User.objects.create_user(username="a", password="pass", role="comptable")
        self.user_a.is_comptable = True
        self.user_a.save()

        self.user_b = User.objects.create_user(username="b", password="pass", role="comptable")
        self.user_b.is_comptable = True
        self.user_b.save()

        # Suppliers
        self.sup_a = Supplier.objects.create(name="SUP A", code="SUPA", is_active=True, siret="12345678901234")
        self.sup_b = Supplier.objects.create(name="SUP B", code="SUPB", is_active=True, siret="22345678901234")

        # Access mapping
        UserSupplierAccess.objects.create(user=self.user_a, supplier=self.sup_a, granted_by=self.admin)
        UserSupplierAccess.objects.create(user=self.user_b, supplier=self.sup_b, granted_by=self.admin)

        # Invoices
        self.inv_a = Invoice.objects.create(supplier=self.sup_a, invoice_number="A1", is_active=True, month=1, year=2026, status="ok", net_to_pay=10)
        self.inv_b = Invoice.objects.create(supplier=self.sup_b, invoice_number="B1", is_active=True, month=1, year=2026, status="ok", net_to_pay=10)

    def test_user_a_cannot_retrieve_user_b_invoice(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse("invoices-detail", kwargs={"pk": self.inv_b.pk})
        r = self.client.get(url)
        self.assertIn(r.status_code, [403, 404])  # 404 acceptable si tu masques l'existence

    def test_admin_can_retrieve_any_invoice(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("invoices-detail", kwargs={"pk": self.inv_b.pk})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_user_a_can_retrieve_own_invoice(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse("invoices-detail", kwargs={"pk": self.inv_a.pk})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
