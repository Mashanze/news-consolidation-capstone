from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.urls import reverse

from .admin import CustomUserAdmin


User = get_user_model()


class RegistrationTests(TestCase):

    def test_registration_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_reader_registration(self):
        response = self.client.post(reverse("register"), {
            "username": "newreader",
            "email": "reader@example.com",
            "role": "reader",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        })

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="newreader")
        self.assertEqual(user.role, "reader")
        self.assertEqual(user.requested_role, "reader")

    def test_journalist_request_does_not_grant_access(self):
        self.client.post(reverse("register"), {
            "username": "newjournalist",
            "email": "journalist@example.com",
            "role": "journalist",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        })

        user = User.objects.get(username="newjournalist")

        self.assertEqual(user.role, "reader")
        self.assertEqual(user.requested_role, "journalist")
        self.assertFalse(user.is_journalist)

    def test_editor_request_does_not_grant_access(self):
        self.client.post(reverse("register"), {
            "username": "neweditor",
            "email": "editor@example.com",
            "role": "editor",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        })

        user = User.objects.get(username="neweditor")

        self.assertEqual(user.role, "reader")
        self.assertEqual(user.requested_role, "editor")
        self.assertFalse(user.is_editor)


class AuthenticationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testreader",
            password="SecurePass123!",
            role="reader",
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.post(reverse("login"), {
            "username": "testreader",
            "password": "SecurePass123!",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            str(self.client.session.get("_auth_user_id")),
            str(self.user.pk),
        )

    def test_logout(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)


class RoleApprovalTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = CustomUserAdmin(User, AdminSite())

        self.superuser = User.objects.create_superuser(
            username="superadmin",
            email="admin@example.com",
            password="SecurePass123!",
        )

        self.staff = User.objects.create_user(
            username="staffuser",
            password="SecurePass123!",
            is_staff=True,
        )

        self.applicant = User.objects.create_user(
            username="applicant",
            password="SecurePass123!",
            role="reader",
            requested_role="journalist",
        )

    def test_staff_cannot_edit_roles(self):
        request = self.factory.get("/admin/")
        request.user = self.staff

        readonly = self.admin.get_readonly_fields(
            request,
            self.applicant,
        )

        self.assertIn("role", readonly)
        self.assertIn("requested_role", readonly)
        self.assertIn("is_superuser", readonly)

    def test_superuser_can_approve_role(self):
        request = self.factory.post("/admin/")
        request.user = self.superuser

        self.admin.message_user = lambda *args, **kwargs: None

        self.admin.approve_requested_roles(
            request,
            User.objects.filter(pk=self.applicant.pk),
        )

        self.applicant.refresh_from_db()

        self.assertEqual(self.applicant.role, "journalist")

    def test_staff_cannot_approve_role(self):
        request = self.factory.post("/admin/")
        request.user = self.staff

        self.admin.message_user = lambda *args, **kwargs: None

        self.admin.approve_requested_roles(
            request,
            User.objects.filter(pk=self.applicant.pk),
        )

        self.applicant.refresh_from_db()

        self.assertEqual(self.applicant.role, "reader")

    def test_superuser_can_reject_role(self):
        request = self.factory.post("/admin/")
        request.user = self.superuser

        self.admin.message_user = lambda *args, **kwargs: None

        self.admin.reject_requested_roles(
            request,
            User.objects.filter(pk=self.applicant.pk),
        )

        self.applicant.refresh_from_db()

        self.assertEqual(self.applicant.role, "reader")
        self.assertEqual(self.applicant.requested_role, "reader")
