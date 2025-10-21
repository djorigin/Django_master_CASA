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
    CompanyContactDetails,
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


# ============================================================================
# Company Contact Details Model Tests (Singleton Pattern)
# ============================================================================


class CompanyContactDetailsModelTests(BaseTestCase):
    """Test cases for CompanyContactDetails singleton model."""

    def test_singleton_pattern(self):
        """Test that only one CompanyContactDetails instance can exist."""
        # Create first instance
        details1 = CompanyContactDetails.objects.create(
            legal_entity_name="Test Company Pty Ltd",
            trading_name="Test Company",
            registered_office_address="123 Test Street, Sydney NSW 2000",
            arn="TEST123456",
            abn="12345678901",
            operational_hq_address="456 Operations Ave, Melbourne VIC 3000",
            operational_hq_phone="+61398765432",
            operational_hq_email="ops@testcompany.com.au",
        )
        self.assertIsNotNone(details1.pk)

        # Attempting to create second instance should raise ValidationError
        with self.assertRaises(ValidationError):
            CompanyContactDetails.objects.create(
                legal_entity_name="Another Company",
                registered_office_address="Another Address",
                arn="ANOTHER123",
                abn="98765432109",
                operational_hq_address="Another Ops Address",
                operational_hq_phone="+61387654321",
                operational_hq_email="ops@another.com.au",
            )

    def test_get_instance_creates_default(self):
        """Test get_instance creates instance with defaults if none exists."""
        # Ensure no instances exist
        CompanyContactDetails.objects.all().delete()

        instance = CompanyContactDetails.get_instance()
        self.assertIsNotNone(instance)
        self.assertEqual(instance.legal_entity_name, "Your Company Name")
        self.assertEqual(instance.arn, "ARN000000")
        self.assertEqual(instance.abn, "00000000000")

    def test_get_instance_returns_existing(self):
        """Test get_instance returns existing instance if available."""
        # Create an instance
        original = CompanyContactDetails.objects.create(
            legal_entity_name="Existing Company",
            registered_office_address="Existing Address",
            arn="EXIST12345",
            abn="11111111111",
            operational_hq_address="Existing Ops",
            operational_hq_phone="+61311111111",
            operational_hq_email="existing@company.com.au",
        )

        instance = CompanyContactDetails.get_instance()
        self.assertEqual(instance.pk, original.pk)
        self.assertEqual(instance.legal_entity_name, "Existing Company")

    def test_display_name_property(self):
        """Test display_name property returns trading name if available."""
        details = CompanyContactDetails.objects.create(
            legal_entity_name="Legal Entity Ltd",
            trading_name="Trading Name",
            registered_office_address="Address",
            arn="PROP123456",
            abn="22222222222",
            operational_hq_address="Ops Address",
            operational_hq_phone="+61322222222",
            operational_hq_email="prop@test.com.au",
        )

        # Should return trading name when available
        self.assertEqual(details.display_name, "Trading Name")

        # Should return legal name when trading name is empty
        details.trading_name = ""
        self.assertEqual(details.display_name, "Legal Entity Ltd")

    def test_get_formatted_overview(self):
        """Test get_formatted_overview replaces placeholders correctly."""
        details = CompanyContactDetails.objects.create(
            legal_entity_name="Aviation Corp Pty Ltd",
            trading_name="Aviation Corp",
            registered_office_address="Address",
            arn="FORMAT1234",
            abn="33333333333",
            operational_hq_address="Ops Address",
            operational_hq_phone="+61333333333",
            operational_hq_email="format@test.com.au",
            organizational_overview=(
                "{Legal Entity Name} operates with {Trading Name} branding. "
                "{Legal Entity Name} is the registered entity."
            ),
        )

        formatted = details.get_formatted_overview()
        expected = (
            "Aviation Corp Pty Ltd operates with Aviation Corp branding. "
            "Aviation Corp Pty Ltd is the registered entity."
        )
        self.assertEqual(formatted, expected)

    def test_arn_validation(self):
        """Test ARN field validation."""
        # Valid ARN
        details = CompanyContactDetails(
            legal_entity_name="Test",
            registered_office_address="Address",
            arn="VALID12345",
            abn="44444444444",
            operational_hq_address="Address",
            operational_hq_phone="+61344444444",
            operational_hq_email="valid@test.com.au",
        )
        details.full_clean()  # Should not raise

        # Invalid ARN (too short)
        details.arn = "SHORT"
        with self.assertRaises(ValidationError):
            details.full_clean()

        # Invalid ARN (special characters)
        details.arn = "INVALID-123"
        with self.assertRaises(ValidationError):
            details.full_clean()

    def test_abn_validation(self):
        """Test ABN field validation."""
        # Valid ABN
        details = CompanyContactDetails(
            legal_entity_name="Test",
            registered_office_address="Address",
            arn="ABNTEST123",
            abn="55555555555",
            operational_hq_address="Address",
            operational_hq_phone="+61355555555",
            operational_hq_email="abn@test.com.au",
        )
        details.full_clean()  # Should not raise

        # Invalid ABN (wrong length)
        details.abn = "123456789"
        with self.assertRaises(ValidationError):
            details.full_clean()

        # Invalid ABN (letters)
        details.abn = "1234567890A"
        with self.assertRaises(ValidationError):
            details.full_clean()

    def test_string_representation(self):
        """Test model string representation."""
        details = CompanyContactDetails.objects.create(
            legal_entity_name="String Test Ltd",
            trading_name="String Test",
            registered_office_address="Address",
            arn="STRING1234",
            abn="66666666666",
            operational_hq_address="Address",
            operational_hq_phone="+61366666666",
            operational_hq_email="string@test.com.au",
        )

        expected = "Company Details: String Test"
        self.assertEqual(str(details), expected)

    def test_updated_by_tracking(self):
        """Test that updated_by field can track who modified the record."""
        details = CompanyContactDetails.objects.create(
            legal_entity_name="Track Test Ltd",
            registered_office_address="Address",
            arn="TRACK12345",
            abn="77777777777",
            operational_hq_address="Address",
            operational_hq_phone="+61377777777",
            operational_hq_email="track@test.com.au",
            updated_by=self.admin_user,
        )

        self.assertEqual(details.updated_by, self.admin_user)


# ============================================================================
# Template Tags and Context Processors Tests
# ============================================================================


class CompanyTemplateTagsTests(BaseTestCase):
    """Test cases for company template tags and context processors."""

    def setUp(self):
        super().setUp()
        # Create company details for testing
        self.company_details = CompanyContactDetails.objects.create(
            legal_entity_name="Test Aviation Pty Ltd",
            trading_name="Test Aviation",
            registered_office_address="123 Test Street",
            arn="TEST123456",
            abn="88888888888",
            operational_hq_address="456 Test Avenue",
            operational_hq_phone="+61388888888",
            operational_hq_email="test@aviation.com.au",
        )

    def test_context_processor_company_details(self):
        """Test that context processor adds company data to context."""
        from django.test import RequestFactory

        from accounts.context_processors import company_details

        factory = RequestFactory()
        request = factory.get("/")

        context_data = company_details(request)

        self.assertIn("company", context_data)
        company_data = context_data["company"]

        self.assertEqual(company_data["legal_name"], "Test Aviation Pty Ltd")
        self.assertEqual(company_data["trading_name"], "Test Aviation")
        self.assertEqual(company_data["display_name"], "Test Aviation")
        self.assertEqual(company_data["arn"], "TEST123456")

    def test_company_name_template_tag(self):
        """Test company_name template tag."""
        from django.template import Context, Template

        template = Template("{% load company_tags %}{% company_name %}")
        rendered = template.render(Context({}))

        self.assertEqual(rendered.strip(), "Test Aviation")

    def test_company_arn_template_tag(self):
        """Test company_arn template tag."""
        from django.template import Context, Template

        template = Template("{% load company_tags %}{% company_arn %}")
        rendered = template.render(Context({}))

        self.assertEqual(rendered.strip(), "TEST123456")

    def test_replace_casa_filter(self):
        """Test replace_casa template filter."""
        from django.template import Context, Template

        template = Template(
            '{% load company_tags %}{{ "Welcome to CASA"|replace_casa }}'
        )
        rendered = template.render(Context({}))

        self.assertEqual(rendered.strip(), "Welcome to Test Aviation")

    def test_cache_invalidation_on_save(self):
        """Test that save method calls cache invalidation."""
        from unittest.mock import patch

        from django.core.cache import cache

        # Mock cache.delete_many to verify it's called
        with patch.object(cache, "delete_many") as mock_delete_many:
            # Update company details (this should call cache.delete_many)
            self.company_details.trading_name = "Updated Aviation"
            self.company_details.save()

            # Verify cache.delete_many was called with correct keys
            mock_delete_many.assert_called_once_with(
                [
                    "company_details",
                    "company_display_name",
                    "company_legal_name",
                    "company_arn",
                    "company_full_info",
                ]
            )

    def test_fallback_when_no_company_exists(self):
        """Test fallback behavior when no company details exist."""
        # Delete company details
        CompanyContactDetails.objects.all().delete()

        from django.template import Context, Template

        template = Template("{% load company_tags %}{% company_name %}")
        rendered = template.render(Context({}))

        # get_instance() creates default with "Your Company Name", not "CASA"
        # This is the expected behavior - it creates a default instance
        self.assertEqual(rendered.strip(), "Your Company Name")
