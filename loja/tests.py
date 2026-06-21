from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .views import DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD


class AdminDemoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username=DEMO_ADMIN_EMAIL,
            email=DEMO_ADMIN_EMAIL,
            password=DEMO_ADMIN_PASSWORD,
            is_staff=True,
        )

    def test_login_exibe_credenciais_de_demonstracao(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, DEMO_ADMIN_EMAIL)
        self.assertContains(response, DEMO_ADMIN_PASSWORD)

    def test_login_redireciona_para_dashboard(self):
        response = self.client.post(reverse("login"), {
            "usuario": DEMO_ADMIN_EMAIL,
            "senha": DEMO_ADMIN_PASSWORD,
        })
        self.assertRedirects(response, reverse("painel"))

    def test_dashboard_e_relatorios_exigem_e_aceitam_staff(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("painel")).status_code, 200)
        self.assertEqual(self.client.get(reverse("relatorios")).status_code, 200)
