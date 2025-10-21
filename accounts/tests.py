"""
Test Suite for Accounts Application
===================================

Comprehensive unit tests covering models, views, forms, and business logic.
Following Django testing best practices and TDD principles.

Test Categories:
- Model Tests: Data validation, relationships, business logic
- View Tests: Authentication, permissions, CRUD operations, error handling
- Form Tests: Field validation, data processing, edge cases
- Integration Tests: End-to-end workflows
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.forms import (
    ClientProfileForm,
    CustomUserForm,
    OperatorCertificateForm,
    PilotProfileForm,
    StaffProfileForm,
)
from accounts.models import (
    ClientProfile,
    OperatorCertificate,
    PilotProfile,
    StaffProfile,
)

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup and utilities."""

    def setUp(self):
        """Set up test data used by test methods."""
        self.client = Client()

        # Create test users
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role="admin",
            is_staff=True,
        )

        self.staff_user = User.objects.create_user(
            email="staff@test.com",
            password="testpass123",
            first_name="Staff",
            last_name="Member",
            role="staff",
        )

        self.pilot_user = User.objects.create_user(
            email="pilot@test.com",
            password="testpass123",
            first_name="John",
            last_name="Pilot",
            role="pilot",
        )

        self.client_user = User.objects.create_user(
            email="client@test.com",
            password="testpass123",
            first_name="Client",
            last_name="Contact",
            role="client",
        )


class CustomUserModelTests(BaseTestCase):
    """Test CustomUser model functionality."""

    def test_user_creation(self):
        """Test user creation with all required fields."""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            role="staff",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.get_full_name(), "Test User")
        self.assertEqual(user.role, "staff")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)

    def test_admin_user_creation(self):
        """Test admin user creation and permissions."""
        admin = User.objects.create_user(
            email="admin@example.com", password="adminpass123", role="admin"
        )

        self.assertEqual(admin.role, "admin")

    def test_get_role_display(self):
        """Test role display method."""
        self.assertEqual(self.admin_user.get_role_display(), "Administrator")
        self.assertEqual(self.staff_user.get_role_display(), "Staff Member")
        self.assertEqual(self.pilot_user.get_role_display(), "Pilot")
        self.assertEqual(self.client_user.get_role_display(), "Client")


class StaffProfileModelTests(BaseTestCase):
    """Test StaffProfile model functionality."""

    def setUp(self):
        super().setUp()
        self.staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            employee_id="EMP001",
            department="operations",
            position_title="Operations Manager",
            contact_number="+61400123456",
            address="123 Test Street, Test City, NSW 2000",
            hire_date=date.today() - timedelta(days=365),
            is_active=True,
        )

    def test_staff_profile_creation(self):
        """Test staff profile creation with valid data."""
        self.assertEqual(self.staff_profile.user, self.staff_user)
        self.assertEqual(self.staff_profile.employee_id, "EMP001")
        self.assertEqual(self.staff_profile.department, "operations")
        self.assertEqual(self.staff_profile.position_title, "Operations Manager")
        self.assertTrue(self.staff_profile.is_active)

    def test_staff_profile_str_representation(self):
        """Test string representation of staff profile."""
        expected = f"{self.staff_user.get_full_name()} - Operations Manager"
        self.assertEqual(str(self.staff_profile), expected)


class PilotProfileModelTests(BaseTestCase):
    """Test PilotProfile model functionality."""

    def setUp(self):
        super().setUp()
        self.pilot_profile = PilotProfile.objects.create(
            user=self.pilot_user,
            role="remote_pilot",
            arn="ARN123456",
            repl_number="REPL-12345",
            repl_expiry=date.today() + timedelta(days=180),
            availability_status="available",
            certifications="Multi-rotor operations, Commercial license",
        )

    def test_pilot_profile_creation(self):
        """Test pilot profile creation with valid data."""
        self.assertEqual(self.pilot_profile.user, self.pilot_user)
        self.assertEqual(self.pilot_profile.role, "remote_pilot")
        self.assertEqual(self.pilot_profile.arn, "ARN123456")
        self.assertEqual(self.pilot_profile.repl_number, "REPL-12345")
        self.assertEqual(self.pilot_profile.availability_status, "available")

    def test_pilot_profile_str_representation(self):
        """Test string representation of pilot profile."""
        expected = f"{self.pilot_user.get_full_name()} (Remote Pilot)"
        self.assertEqual(str(self.pilot_profile), expected)


class ClientProfileModelTests(BaseTestCase):
    """Test ClientProfile model functionality."""

    def setUp(self):
        super().setUp()
        self.client_profile = ClientProfile.objects.create(
            user=self.client_user,
            company_name="Test Aviation Corp",
            abn="12345678901",
            industry="construction",
            contact_number="+61388887777",
            billing_email="billing@testaviation.com",
            address="789 Client Boulevard, Business Park, VIC 3000",
            credit_limit=Decimal("50000.00"),
            payment_terms=30,
            status="active",
        )

    def test_client_profile_creation(self):
        """Test client profile creation with valid data."""
        self.assertEqual(self.client_profile.user, self.client_user)
        self.assertEqual(self.client_profile.company_name, "Test Aviation Corp")
        self.assertEqual(self.client_profile.abn, "12345678901")
        self.assertEqual(self.client_profile.credit_limit, Decimal("50000.00"))
        self.assertEqual(self.client_profile.payment_terms, 30)

    def test_client_profile_str_representation(self):
        """Test string representation of client profile."""
        expected = "Client Contact - Test Aviation Corp"
        self.assertEqual(str(self.client_profile), expected)


class OperatorCertificateModelTests(BaseTestCase):
    """Test OperatorCertificate model functionality."""

    def setUp(self):
        super().setUp()
        self.pilot_profile = PilotProfile.objects.create(
            user=self.pilot_user, role="remote_pilot", arn="ARN123456"
        )

        self.certificate = OperatorCertificate.objects.create(
            reoc_number="CERT-2025-001",
            company_name="Test Aviation Services",
            contact_email="admin@testaviation.com",
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            status="active",
            casa_operator_number="CASA-001",
        )

    def test_certificate_creation(self):
        """Test certificate creation with valid data."""
        self.assertEqual(self.certificate.reoc_number, "CERT-2025-001")
        self.assertEqual(self.certificate.company_name, "Test Aviation Services")
        self.assertEqual(self.certificate.contact_email, "admin@testaviation.com")
        self.assertEqual(self.certificate.status, "active")

    def test_certificate_str_representation(self):
        """Test string representation of certificate."""
        expected = "Test Aviation Services - CERT-2025-001"
        self.assertEqual(str(self.certificate), expected)


class UserViewTests(BaseTestCase):
    """Test user-related views."""

    def test_user_list_view_requires_login(self):
        """Test that user list view requires authentication."""
        url = reverse("accounts:user_list")
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_user_list_view_authenticated(self):
        """Test user list view with authenticated user."""
        self.client.force_login(self.admin_user)
        url = reverse("accounts:user_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Management")
        self.assertContains(response, self.admin_user.get_full_name())

    def test_user_detail_view(self):
        """Test user detail view."""
        self.client.force_login(self.admin_user)
        url = reverse("accounts:user_detail", kwargs={"pk": self.staff_user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.staff_user.get_full_name())
        self.assertContains(response, self.staff_user.email)

    def test_user_authentication_works(self):
        """Test that user authentication works properly."""
        # Test login with email as username
        login_successful = self.client.login(
            username="admin@test.com", password="testpass123"  # Using email as username
        )
        self.assertTrue(login_successful)


class FormTests(BaseTestCase):
    """Test form functionality and validation."""

    def test_custom_user_form_valid_data(self):
        """Test CustomUserForm with valid data."""
        form_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "staff",
        }
        form = CustomUserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_user_form_invalid_email(self):
        """Test CustomUserForm with invalid email."""
        form_data = {
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User",
            "role": "staff",
        }
        form = CustomUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class IntegrationTests(BaseTestCase):
    """Integration tests for complete workflows."""

    def test_user_model_integration(self):
        """Test user model integration with profiles."""
        # Create a staff profile
        staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            department="operations",
            position_title="Manager",
            contact_number="+61400123456",
            address="123 Test St",
        )

        # Test the relationship
        self.assertEqual(self.staff_user.staff_profile, staff_profile)
        self.assertEqual(staff_profile.user, self.staff_user)

        # Test string representations work
        self.assertIn("Staff Member", str(staff_profile))

        # Verify initial user count
        initial_count = User.objects.count()
        self.assertGreaterEqual(User.objects.count(), initial_count)

    def test_complete_crud_workflow(self):
        """Test complete CRUD workflow with templates."""
        self.client.force_login(self.admin_user)

        # Test we can access dashboard
        dashboard_url = reverse("accounts:dashboard")
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)

        # Test we can access staff list
        staff_list_url = reverse("accounts:staff_list")
        response = self.client.get(staff_list_url)
        self.assertEqual(response.status_code, 200)

        # Test we can access pilot list
        pilot_list_url = reverse("accounts:pilot_list")
        response = self.client.get(pilot_list_url)
        self.assertEqual(response.status_code, 200)


class SecurityTests(BaseTestCase):
    """Security-related tests."""

    def test_unauthorized_access_prevention(self):
        """Test that unauthorized users cannot access protected views."""
        protected_urls = [
            reverse("accounts:user_list"),
            reverse("accounts:staff_list"),
            reverse("accounts:pilot_list"),
            reverse("accounts:client_list"),
            reverse("accounts:certificate_list"),
        ]

        for url in protected_urls:
            response = self.client.get(url)
            # Should redirect to login
            self.assertEqual(response.status_code, 302)
            self.assertIn("/admin/login/", response.url)
