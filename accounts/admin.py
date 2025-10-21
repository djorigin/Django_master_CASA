from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    ClientProfile,
    CompanyContactDetails,
    CustomUser,
    OperatorCertificate,
    PilotProfile,
    StaffProfile,
)


class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = (
        "email",
        "get_full_name",
        "role",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "is_staff", "is_active", "date_joined")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name", "role")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("date_joined", "last_login")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "position_title",
        "department",
        "contact_number",
        "is_active",
        "hire_date",
    )
    list_filter = ("department", "is_active", "hire_date")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "position_title",
        "department",
    )
    readonly_fields = ()
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (
            _("Job Details"),
            {
                "fields": (
                    "position_title",
                    "department",
                    "employee_id",
                    "hire_date",
                    "is_active",
                )
            },
        ),
        (_("Contact Information"), {"fields": ("contact_number", "address")}),
        (_("Documents"), {"fields": ("photo_id",)}),
    )


@admin.register(PilotProfile)
class PilotProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "arn",
        "availability_status",
        "is_repl_expired",
        "repl_expiry",
    )
    list_filter = ("role", "availability_status", "repl_expiry")
    search_fields = ("user__first_name", "user__last_name", "arn", "repl_number")
    readonly_fields = ("created_at", "updated_at", "is_repl_expired", "is_available")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (_("Pilot Details"), {"fields": ("role", "arn", "availability_status")}),
        (
            _("Licenses & Certifications"),
            {
                "fields": (
                    "repl_number",
                    "repl_expiry",
                    "medical_clearance_date",
                    "certifications",
                )
            },
        ),
        (
            _("Contact Information"),
            {"fields": ("contact_number", "address", "home_base_location")},
        ),
        (
            _("Emergency Contact"),
            {"fields": ("emergency_contact_name", "emergency_contact_phone")},
        ),
        (_("Documents"), {"fields": ("photo_id",)}),
        (_("Additional Information"), {"fields": ("notes",)}),
        (
            _("System Information"),
            {
                "fields": (
                    "is_repl_expired",
                    "is_available",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def is_repl_expired(self, obj):
        if obj.is_repl_expired is None:
            return "-"
        elif obj.is_repl_expired:
            return format_html(
                '<span style="color: red; font-weight: bold;">Expired</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">Valid</span>'
            )

    is_repl_expired.short_description = _("REPL Status")


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "company_name",
        "industry",
        "status",
        "account_manager",
        "created_at",
    )
    list_filter = ("industry", "status", "created_at")
    search_fields = ("user__first_name", "user__last_name", "company_name", "abn")
    readonly_fields = ("created_at", "updated_at", "is_active")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (
            _("Company Details"),
            {"fields": ("company_name", "abn", "industry", "status")},
        ),
        (
            _("Business Information"),
            {"fields": ("credit_limit", "payment_terms", "account_manager")},
        ),
        (
            _("Contact Information"),
            {"fields": ("contact_number", "billing_email", "address")},
        ),
        (_("Documents"), {"fields": ("photo_id",)}),
        (_("Additional Information"), {"fields": ("notes",)}),
        (
            _("System Information"),
            {
                "fields": ("is_active", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(OperatorCertificate)
class OperatorCertificateAdmin(admin.ModelAdmin):
    list_display = (
        "reoc_number",
        "company_name",
        "status",
        "issue_date",
        "expiry_date",
        "is_expired",
        "days_until_expiry",
    )
    list_filter = ("status", "issue_date", "expiry_date")
    search_fields = ("reoc_number", "company_name", "casa_operator_number")
    readonly_fields = ("created_at", "updated_at", "is_expired", "days_until_expiry")
    fieldsets = (
        (
            _("Certificate Information"),
            {"fields": ("reoc_number", "casa_operator_number", "status")},
        ),
        (_("Company Information"), {"fields": ("company_name", "contact_email")}),
        (_("Validity Period"), {"fields": ("issue_date", "expiry_date")}),
        (
            _("System Information"),
            {
                "fields": (
                    "is_expired",
                    "days_until_expiry",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def is_expired(self, obj):
        if obj.is_expired:
            return format_html(
                '<span style="color: red; font-weight: bold;">Expired</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">Valid</span>'
            )

    is_expired.short_description = _("Certificate Status")


@admin.register(CompanyContactDetails)
class CompanyContactDetailsAdmin(admin.ModelAdmin):
    """
    Admin interface for Company Contact Details (Singleton model).
    """

    fieldsets = (
        (
            _("Legal Information"),
            {
                "fields": (
                    "legal_entity_name",
                    "trading_name",
                    "arn",
                    "abn",
                ),
                "description": "Official legal and registration information",
            },
        ),
        (
            _("Addresses"),
            {
                "fields": (
                    "registered_office_address",
                    "operational_hq_address",
                ),
                "description": "Physical addresses for legal and operational purposes",
            },
        ),
        (
            _("Contact Information"),
            {
                "fields": (
                    "operational_hq_phone",
                    "operational_hq_email",
                ),
                "description": "Primary contact details for operations",
            },
        ),
        (
            _("Organizational Overview"),
            {
                "fields": ("organizational_overview",),
                "description": "Company description and operational capabilities",
            },
        ),
        (
            _("Metadata"),
            {
                "fields": (
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        """
        Prevent adding new instances if one already exists.
        """
        if CompanyContactDetails.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of company contact details.
        """
        return False

    def save_model(self, request, obj, form, change):
        """
        Automatically set the updated_by field to current user.
        """
        if hasattr(obj, "updated_by"):
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        """
        Redirect to the edit form if instance exists, otherwise show add form.
        """
        try:
            instance = CompanyContactDetails.get_instance()
            from django.http import HttpResponseRedirect
            from django.urls import reverse

            return HttpResponseRedirect(
                reverse(
                    "admin:accounts_companycontactdetails_change", args=[instance.pk]
                )
            )
        except Exception:
            return super().changelist_view(request, extra_context)


admin.site.register(CustomUser, CustomUserAdmin)
