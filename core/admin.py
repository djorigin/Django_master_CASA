from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    ManualApprovalHistory,
    ManualDistributionRecord,
    ManualSection,
    ManualSubsection,
    RPASOperationsManual,
    SOPProcedureStep,
    SOPRiskAssessment,
    StandardOperatingProcedure,
    TrainingRegister,
    TrainingSyllabus,
)


class SOPProcedureStepInline(admin.TabularInline):
    """Inline admin for SOP Procedure Steps"""

    model = SOPProcedureStep
    extra = 1
    fields = [
        "step_number",
        "step_type",
        "title",
        "responsible_role",
        "safety_critical",
        "verification_required",
    ]
    ordering = ["step_number"]


class SOPRiskAssessmentInline(admin.TabularInline):
    """Inline admin for SOP Risk Assessments"""

    model = SOPRiskAssessment
    extra = 0
    fields = ["risk_register", "risk_context", "risk_owner", "next_review_date"]
    readonly_fields = ["assessed_date"]


@admin.register(StandardOperatingProcedure)
class StandardOperatingProcedureAdmin(admin.ModelAdmin):
    """
    Admin interface for Standard Operating Procedures
    CASA-compliant SOP management
    """

    list_display = [
        "sop_id",
        "title",
        "category",
        "version",
        "status_display",
        "priority_display",
        "steps_count",
        "risk_count",
        "approval_status_display",
        "next_review_date",
    ]

    list_filter = [
        "category",
        "status",
        "priority",
        "frequency_of_use",
        "created_date",
        "next_review_date",
    ]

    search_fields = [
        "sop_id",
        "title",
        "purpose",
        "scope",
        "created_by__user__first_name",
        "created_by__user__last_name",
    ]

    fieldsets = (
        (
            "SOP Identification",
            {
                "fields": (
                    "sop_id",
                    "title",
                    "category",
                    "version",
                    "priority",
                    "frequency_of_use",
                ),
                "description": "Basic SOP identification and categorization",
            },
        ),
        (
            "CASA Compliance Requirements",
            {
                "fields": (
                    "purpose",
                    "scope",
                    "responsibilities",
                    "definitions",
                    "references",
                ),
                "description": "CASA regulatory compliance documentation",
            },
        ),
        (
            "Operational Details",
            {
                "fields": ("aircraft_types", "status"),
                "description": "Operational applicability and current status",
            },
        ),
        (
            "Review and Approval",
            {
                "fields": (
                    "created_by",
                    "reviewed_by",
                    "approved_by",
                    "reviewed_date",
                    "approved_date",
                    "effective_date",
                    "next_review_date",
                ),
                "description": "CASA approval and review tracking",
            },
        ),
        (
            "Version Control",
            {
                "fields": ("superseded_by", "supersedes"),
                "classes": ("collapse",),
                "description": "SOP version control and supersession",
            },
        ),
    )

    readonly_fields = ["created_date", "updated_at"]
    filter_horizontal = ["aircraft_types"]
    inlines = [SOPProcedureStepInline, SOPRiskAssessmentInline]

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            "approved": "green",
            "draft": "orange",
            "review": "blue",
            "revision": "red",
            "superseded": "gray",
            "withdrawn": "darkred",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def priority_display(self, obj):
        """Display priority with color coding"""
        colors = {"critical": "red", "high": "orange", "medium": "blue", "low": "green"}
        color = colors.get(obj.priority, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display(),
        )

    priority_display.short_description = "Priority"

    def steps_count(self, obj):
        """Display number of procedure steps"""
        count = obj.procedure_steps_count
        return format_html('<span style="font-weight: bold;">{}</span>', count)

    steps_count.short_description = "Steps"

    def risk_count(self, obj):
        """Display number of risk assessments"""
        count = obj.risk_assessments.count()
        if count > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>', count
            )
        return format_html('<span style="color: gray;">0</span>')

    risk_count.short_description = "Risks"

    def approval_status_display(self, obj):
        """Display approval status"""
        if obj.status == "approved" and obj.approved_by:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                obj.approved_by.user.get_full_name(),
            )
        elif obj.status == "review" and obj.reviewed_by:
            return format_html('<span style="color: blue;">⏳ Under Review</span>')
        else:
            return format_html('<span style="color: orange;">⚠ Pending</span>')

    approval_status_display.short_description = "Approval"


@admin.register(SOPProcedureStep)
class SOPProcedureStepAdmin(admin.ModelAdmin):
    """
    Admin interface for SOP Procedure Steps
    """

    list_display = [
        "sop_display",
        "step_number",
        "title",
        "step_type",
        "responsible_role",
        "safety_critical_display",
        "verification_required_display",
        "duration_estimate",
    ]

    list_filter = [
        "step_type",
        "safety_critical",
        "verification_required",
        "sop__category",
        "sop__status",
    ]

    search_fields = [
        "sop__sop_id",
        "sop__title",
        "title",
        "description",
        "responsible_role",
    ]

    fieldsets = (
        (
            "Step Identification",
            {"fields": ("sop", "step_number", "step_type", "title")},
        ),
        (
            "Step Details",
            {"fields": ("description", "responsible_role", "duration_estimate")},
        ),
        (
            "Safety and Verification",
            {"fields": ("safety_critical", "verification_required", "notes")},
        ),
        ("Dependencies", {"fields": ("prerequisite_steps",), "classes": ("collapse",)}),
    )

    filter_horizontal = ["prerequisite_steps"]

    def sop_display(self, obj):
        """Display SOP with link"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:core_standardoperatingprocedure_change", args=[obj.sop.pk]),
            obj.sop.sop_id,
        )

    sop_display.short_description = "SOP"

    def safety_critical_display(self, obj):
        """Display safety critical status"""
        if obj.safety_critical:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ CRITICAL</span>'
            )
        return format_html('<span style="color: green;">✓ Normal</span>')

    safety_critical_display.short_description = "Safety"

    def verification_required_display(self, obj):
        """Display verification requirement"""
        if obj.verification_required:
            return format_html(
                '<span style="color: blue; font-weight: bold;">✓ Required</span>'
            )
        return format_html('<span style="color: gray;">Not Required</span>')

    verification_required_display.short_description = "Verification"


@admin.register(SOPRiskAssessment)
class SOPRiskAssessmentAdmin(admin.ModelAdmin):
    """
    Admin interface for SOP Risk Assessments
    """

    list_display = [
        "sop_display",
        "risk_hazard",
        "risk_level_display",
        "risk_owner",
        "next_review_date",
        "mitigation_steps_count",
    ]

    list_filter = [
        "risk_register__risk_level",
        "sop__category",
        "next_review_date",
        "assessed_date",
    ]

    search_fields = [
        "sop__sop_id",
        "sop__title",
        "risk_register__hazard",
        "risk_context",
        "risk_owner__user__first_name",
        "risk_owner__user__last_name",
    ]

    fieldsets = (
        ("Risk Assessment Link", {"fields": ("sop", "risk_register")}),
        (
            "SOP-Specific Risk Information",
            {"fields": ("risk_context", "monitoring_requirements", "risk_owner")},
        ),
        (
            "Mitigation",
            {
                "fields": ("mitigation_steps",),
            },
        ),
        (
            "Review Schedule",
            {"fields": ("next_review_date", "assessed_date", "last_reviewed")},
        ),
    )

    readonly_fields = ["assessed_date", "last_reviewed"]
    filter_horizontal = ["mitigation_steps"]

    def sop_display(self, obj):
        """Display SOP with link"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:core_standardoperatingprocedure_change", args=[obj.sop.pk]),
            obj.sop.sop_id,
        )

    sop_display.short_description = "SOP"

    def risk_hazard(self, obj):
        """Display risk hazard"""
        return obj.risk_register.hazard[:50] + (
            "..." if len(obj.risk_register.hazard) > 50 else ""
        )

    risk_hazard.short_description = "Hazard"

    def risk_level_display(self, obj):
        """Display risk level with color"""
        risk_level = obj.risk_register.risk_level
        colors = {"low": "green", "medium": "orange", "high": "red"}
        color = colors.get(risk_level, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            risk_level.upper(),
        )

    risk_level_display.short_description = "Risk Level"

    def mitigation_steps_count(self, obj):
        """Display count of mitigation steps"""
        count = obj.mitigation_steps.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)

    mitigation_steps_count.short_description = "Mitigation Steps"


class TrainingRegisterInline(admin.TabularInline):
    """Inline admin for Training Records"""

    model = TrainingRegister
    extra = 0
    fields = [
        "training_record_id",
        "trainee_pilot",
        "trainee_staff",
        "required_by_date",
        "status",
        "priority",
    ]
    readonly_fields = ["training_record_id"]


@admin.register(TrainingSyllabus)
class TrainingSyllabusAdmin(admin.ModelAdmin):
    """
    Admin interface for Training Syllabus Management
    CASA-compliant training curriculum management
    """

    list_display = [
        "syllabus_id",
        "title",
        "category",
        "training_type",
        "applicability_display",
        "duration_hours",
        "status_display",
        "regulatory_requirement_display",
        "training_records_count_display",
        "approved_date",
    ]

    list_filter = [
        "category",
        "training_type",
        "applicability",
        "status",
        "regulatory_requirement",
        "recurrent_training_required",
        "approved_date",
    ]

    search_fields = [
        "syllabus_id",
        "title",
        "description",
        "learning_objectives",
        "casa_reference",
        "created_by__user__first_name",
        "created_by__user__last_name",
    ]

    fieldsets = (
        (
            "Syllabus Identification",
            {
                "fields": (
                    "syllabus_id",
                    "title",
                    "category",
                    "training_type",
                    "applicability",
                ),
                "description": "Basic training syllabus identification",
            },
        ),
        (
            "Training Content",
            {
                "fields": (
                    "description",
                    "learning_objectives",
                    "prerequisites",
                    "competency_standards",
                ),
                "description": "Training curriculum and learning objectives",
            },
        ),
        (
            "Training Delivery",
            {
                "fields": (
                    "duration_hours",
                    "theory_hours",
                    "practical_hours",
                    "assessment_method",
                    "pass_mark",
                ),
                "description": "Training delivery and assessment parameters",
            },
        ),
        (
            "CASA Compliance",
            {
                "fields": (
                    "casa_reference",
                    "regulatory_requirement",
                    "validity_period_months",
                    "recurrent_training_required",
                ),
                "description": "CASA regulatory compliance requirements",
            },
        ),
        (
            "Applicability",
            {
                "fields": ("aircraft_types",),
                "description": "Aircraft types this training applies to",
            },
        ),
        (
            "Approval",
            {
                "fields": ("status", "approved_by", "approved_date", "created_by"),
                "description": "Training syllabus approval and status",
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["aircraft_types"]
    inlines = [TrainingRegisterInline]

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            "current": "green",
            "approved": "blue",
            "draft": "orange",
            "superseded": "gray",
            "withdrawn": "red",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def applicability_display(self, obj):
        """Display applicability in short form"""
        applicability_short = {
            "all_rps": "All RPs",
            "rps_operating_rpa": "RPA Operators",
            "operational_crew": "Ops Crew",
            "rps_night_ops": "Night Ops",
            "maintenance_staff": "Maintenance",
            "safety_officers": "Safety",
        }
        return applicability_short.get(
            obj.applicability, obj.get_applicability_display()
        )

    applicability_display.short_description = "Applies To"

    def regulatory_requirement_display(self, obj):
        """Display regulatory requirement status"""
        if obj.regulatory_requirement:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ MANDATORY</span>'
            )
        return format_html('<span style="color: blue;">Optional</span>')

    regulatory_requirement_display.short_description = "Regulatory"

    def training_records_count_display(self, obj):
        """Display count of training records"""
        count = obj.training_records_count
        return format_html('<span style="font-weight: bold;">{}</span>', count)

    training_records_count_display.short_description = "Records"


@admin.register(TrainingRegister)
class TrainingRegisterAdmin(admin.ModelAdmin):
    """
    Admin interface for Training Register
    Comprehensive training tracking and compliance management
    """

    list_display = [
        "training_record_id",
        "trainee_display",
        "training_syllabus_display",
        "status_display",
        "priority_display",
        "required_by_date",
        "completion_status",
        "validity_status",
        "days_remaining",
    ]

    list_filter = [
        "status",
        "priority",
        "training_syllabus__category",
        "training_syllabus__regulatory_requirement",
        "passed",
        "required_by_date",
        "valid_until",
    ]

    search_fields = [
        "training_record_id",
        "trainee_pilot__user__first_name",
        "trainee_pilot__user__last_name",
        "trainee_staff__user__first_name",
        "trainee_staff__user__last_name",
        "training_syllabus__title",
        "training_syllabus__syllabus_id",
        "certificate_number",
    ]

    fieldsets = (
        (
            "Training Record",
            {
                "fields": (
                    "training_record_id",
                    "training_syllabus",
                    "trainee_pilot",
                    "trainee_staff",
                ),
                "description": "Basic training record identification",
            },
        ),
        (
            "Scheduling",
            {
                "fields": ("status", "priority", "required_by_date", "scheduled_date"),
                "description": "Training scheduling and priority",
            },
        ),
        (
            "Training Delivery",
            {
                "fields": (
                    "instructor",
                    "training_provider",
                    "training_location",
                    "started_date",
                    "completed_date",
                ),
                "description": "Training delivery details",
            },
        ),
        (
            "Assessment",
            {
                "fields": (
                    "assessment_score",
                    "passed",
                    "certificate_number",
                    "training_notes",
                ),
                "description": "Assessment results and certification",
            },
        ),
        (
            "Validity Tracking",
            {
                "fields": ("valid_from", "valid_until", "next_recurrent_due"),
                "description": "Training validity and recurrency tracking",
            },
        ),
        ("Administrative", {"fields": ("created_by",), "classes": ("collapse",)}),
    )

    readonly_fields = ["training_record_id", "created_at", "updated_at"]

    def trainee_display(self, obj):
        """Display trainee name with role"""
        trainee = obj.get_trainee_profile()
        if obj.trainee_pilot:
            role_badge = '<span style="background: blue; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">PILOT</span>'
        else:
            role_badge = '<span style="background: green; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">STAFF</span>'

        return format_html("{} {}", role_badge, obj.get_trainee_name())

    trainee_display.short_description = "Trainee"

    def training_syllabus_display(self, obj):
        """Display training syllabus with link"""
        return format_html(
            '<a href="{}" title="{}">{}</a>',
            reverse(
                "admin:core_trainingsyllabus_change", args=[obj.training_syllabus.pk]
            ),
            obj.training_syllabus.title,
            obj.training_syllabus.syllabus_id,
        )

    training_syllabus_display.short_description = "Training"

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            "completed": "green",
            "in_progress": "blue",
            "scheduled": "orange",
            "required": "red",
            "failed": "darkred",
            "expired": "gray",
            "waived": "purple",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def priority_display(self, obj):
        """Display priority with color coding"""
        colors = {"critical": "red", "high": "orange", "medium": "blue", "low": "green"}
        color = colors.get(obj.priority, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display(),
        )

    priority_display.short_description = "Priority"

    def completion_status(self, obj):
        """Display completion status"""
        if obj.status == "completed":
            if obj.assessment_score:
                return format_html(
                    '<span style="color: green;">✓ {}%</span>', obj.assessment_score
                )
            return format_html('<span style="color: green;">✓ Completed</span>')
        elif obj.status == "failed":
            if obj.assessment_score:
                return format_html(
                    '<span style="color: red;">✗ {}%</span>', obj.assessment_score
                )
            return format_html('<span style="color: red;">✗ Failed</span>')
        else:
            return format_html('<span style="color: gray;">Pending</span>')

    completion_status.short_description = "Result"

    def validity_status(self, obj):
        """Display validity status"""
        if obj.valid_until:
            if obj.is_expired:
                return format_html(
                    '<span style="color: red; font-weight: bold;">⚠ EXPIRED</span>'
                )
            else:
                return format_html(
                    '<span style="color: green;">Valid until {}</span>',
                    obj.valid_until.strftime("%d/%m/%Y"),
                )
        return format_html('<span style="color: gray;">N/A</span>')

    validity_status.short_description = "Validity"

    def days_remaining(self, obj):
        """Display days until due"""
        days = obj.days_until_due
        if days is None:
            return format_html('<span style="color: gray;">N/A</span>')

        if days < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">{} days OVERDUE</span>',
                abs(days),
            )
        elif days <= 7:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{} days</span>', days
            )
        else:
            return format_html('<span style="color: green;">{} days</span>', days)

    days_remaining.short_description = "Due In"


# RPAS Operations Manual Admin Interfaces


class ManualSubsectionInline(admin.TabularInline):
    """Inline admin for Manual Subsections"""

    model = ManualSubsection
    extra = 1
    fields = ["subsection_number", "title", "order", "casa_reference"]
    ordering = ["order", "subsection_number"]


class ManualSectionInline(admin.StackedInline):
    """Inline admin for Manual Sections"""

    model = ManualSection
    extra = 1
    fields = [
        ("section_number", "title"),
        ("section_type", "order"),
        "content",
        ("related_sops", "required_training"),
    ]
    filter_horizontal = ["related_sops", "required_training"]
    ordering = ["order", "section_number"]


class ManualApprovalHistoryInline(admin.TabularInline):
    """Inline admin for Manual Approval History"""

    model = ManualApprovalHistory
    extra = 0
    fields = ["action", "action_date", "performed_by", "version_at_action", "comments"]
    readonly_fields = ["action_date"]
    ordering = ["-action_date"]

    def has_add_permission(self, request, obj=None):
        # Approval history is added automatically
        return False


class ManualDistributionRecordInline(admin.TabularInline):
    """Inline admin for Manual Distribution Records"""

    model = ManualDistributionRecord
    extra = 1
    fields = [
        "distributed_to",
        "version_distributed",
        "access_granted_by",
        "acknowledgment_required",
        "acknowledged_date",
        "access_revoked",
    ]
    readonly_fields = ["distribution_date"]


@admin.register(RPASOperationsManual)
class RPASOperationsManualAdmin(admin.ModelAdmin):
    """
    Admin interface for RPAS Operations Manual
    Comprehensive document management with CASA compliance
    """

    list_display = [
        "manual_id",
        "title",
        "manual_type",
        "version_display",
        "status_display",
        "casa_approval_status",
        "effective_display",
        "review_status",
    ]

    list_filter = [
        "manual_type",
        "status",
        "casa_approved",
        "effective_date",
        "next_review_date",
    ]

    search_fields = [
        "manual_id",
        "title",
        "organization_name",
        "casa_approval_reference",
    ]

    fieldsets = (
        (
            "Document Identification",
            {
                "fields": (
                    ("manual_id", "title"),
                    ("manual_type", "version"),
                    ("revision_number", "status"),
                ),
                "description": "Basic document identification and classification",
            },
        ),
        (
            "Document Control",
            {
                "fields": (
                    ("effective_date", "next_review_date"),
                    ("supersedes_version", "change_summary"),
                    ("controlled_distribution", "digital_signature_required"),
                ),
                "description": "Document control and version management",
            },
        ),
        (
            "CASA Compliance",
            {
                "fields": (
                    ("casa_approved", "casa_approval_reference"),
                    "casa_approval_date",
                    "applicable_regulations",
                ),
                "description": "CASA regulatory approval and compliance",
            },
        ),
        (
            "Organization Details",
            {
                "fields": (
                    ("organization_name", "reoc_number"),
                    ("purpose", "abstract"),
                ),
                "description": "Organizational information and document purpose",
            },
        ),
        (
            "Approval Chain",
            {
                "fields": (
                    "prepared_by",
                    "reviewed_by",
                    ("approved_by", "approval_date"),
                ),
                "description": "Document preparation and approval workflow",
            },
        ),
        (
            "Integration",
            {
                "fields": ("related_sops", "training_syllabus"),
                "description": "Integration with SOPs and training systems",
                "classes": ("collapse",),
            },
        ),
    )

    filter_horizontal = ["related_sops", "training_syllabus"]
    readonly_fields = ["manual_id"]
    inlines = [
        ManualSectionInline,
        ManualApprovalHistoryInline,
        ManualDistributionRecordInline,
    ]

    def get_queryset(self, request):
        """Optimize queries"""
        return (
            super()
            .get_queryset(request)
            .select_related("prepared_by", "reviewed_by", "approved_by")
            .prefetch_related("sections", "approval_history")
        )

    def version_display(self, obj):
        """Display version with revision number"""
        if obj.revision_number > 0:
            return format_html(
                "<strong>{}r{}</strong>", obj.version, obj.revision_number
            )
        return format_html("<strong>{}</strong>", obj.version)

    version_display.short_description = "Version"

    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            "draft": "gray",
            "review": "orange",
            "approved": "blue",
            "published": "green",
            "superseded": "purple",
            "withdrawn": "red",
        }
        color = colors.get(obj.status, "black")

        # Add icons for visual clarity
        icons = {
            "draft": "📝",
            "review": "👀",
            "approved": "✅",
            "published": "📚",
            "superseded": "⏏️",
            "withdrawn": "🚫",
        }
        icon = icons.get(obj.status, "📄")

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def casa_approval_status(self, obj):
        """Display CASA approval status"""
        if obj.casa_approved:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ CASA Approved</span><br>'
                "<small>{}</small>",
                obj.casa_approval_reference or "No reference",
            )
        else:
            return format_html('<span style="color: gray;">⏳ Pending CASA</span>')

    casa_approval_status.short_description = "CASA Status"

    def effective_display(self, obj):
        """Display effective date status"""
        today = timezone.now().date()

        if obj.effective_date <= today:
            if obj.status == "published":
                return format_html(
                    '<span style="color: green;">✓ Effective</span><br>'
                    "<small>{}</small>",
                    obj.effective_date.strftime("%d/%m/%Y"),
                )
            else:
                return format_html(
                    '<span style="color: orange;">⚠ Not Published</span><br>'
                    "<small>{}</small>",
                    obj.effective_date.strftime("%d/%m/%Y"),
                )
        else:
            return format_html(
                '<span style="color: blue;">⏰ Future</span><br>' "<small>{}</small>",
                obj.effective_date.strftime("%d/%m/%Y"),
            )

    effective_display.short_description = "Effective"

    def review_status(self, obj):
        """Display review status"""
        days_until = obj.days_until_review

        if days_until is None:
            return format_html('<span style="color: gray;">N/A</span>')

        if days_until < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ OVERDUE</span><br>'
                "<small>{} days</small>",
                abs(days_until),
            )
        elif days_until <= 30:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠ Due Soon</span><br>'
                "<small>{} days</small>",
                days_until,
            )
        else:
            return format_html(
                '<span style="color: green;">✓ Current</span><br>'
                "<small>{} days</small>",
                days_until,
            )

    review_status.short_description = "Review Status"


@admin.register(ManualSection)
class ManualSectionAdmin(admin.ModelAdmin):
    """Admin interface for Manual Sections"""

    list_display = [
        "section_display",
        "operations_manual",
        "section_type",
        "sop_count",
        "training_count",
    ]

    list_filter = [
        "section_type",
        "operations_manual__manual_type",
        "operations_manual__status",
    ]

    search_fields = ["title", "section_number", "operations_manual__title"]

    fieldsets = (
        (
            "Section Details",
            {
                "fields": (
                    ("operations_manual", "section_type"),
                    ("section_number", "title"),
                    "order",
                    "content",
                )
            },
        ),
        (
            "Integration",
            {
                "fields": ("related_sops", "required_training"),
                "description": "Related procedures and training requirements",
            },
        ),
    )

    filter_horizontal = ["related_sops", "required_training"]
    inlines = [ManualSubsectionInline]

    def section_display(self, obj):
        """Display section with number and title"""
        return format_html(
            "<strong>Section {}</strong><br><em>{}</em>", obj.section_number, obj.title
        )

    section_display.short_description = "Section"

    def sop_count(self, obj):
        """Count of related SOPs"""
        count = obj.related_sops.count()
        if count > 0:
            return format_html('<span style="color: blue;">{} SOPs</span>', count)
        return format_html('<span style="color: gray;">No SOPs</span>')

    sop_count.short_description = "SOPs"

    def training_count(self, obj):
        """Count of related training"""
        count = obj.required_training.count()
        if count > 0:
            return format_html('<span style="color: green;">{} Training</span>', count)
        return format_html('<span style="color: gray;">No Training</span>')

    training_count.short_description = "Training"


@admin.register(ManualSubsection)
class ManualSubsectionAdmin(admin.ModelAdmin):
    """Admin interface for Manual Subsections"""

    list_display = [
        "subsection_display",
        "section",
        "casa_reference_display",
        "content_length",
    ]

    list_filter = ["section__section_type", "section__operations_manual__manual_type"]

    search_fields = ["title", "subsection_number", "casa_reference", "content"]

    fieldsets = (
        (
            "Subsection Details",
            {
                "fields": (
                    ("section", "subsection_number"),
                    "title",
                    "order",
                    "casa_reference",
                )
            },
        ),
        (
            "Content",
            {
                "fields": ("content",),
                "description": "Detailed subsection content (HTML/Markdown supported)",
            },
        ),
    )

    def subsection_display(self, obj):
        """Display subsection with number and title"""
        return format_html(
            "<strong>{}</strong><br><em>{}</em>", obj.subsection_number, obj.title
        )

    subsection_display.short_description = "Subsection"

    def casa_reference_display(self, obj):
        """Display CASA reference with formatting"""
        if obj.casa_reference:
            return format_html(
                '<span style="background-color: #e8f5e8; padding: 2px 6px; border-radius: 3px;">'
                "CASA {}</span>",
                obj.casa_reference,
            )
        return format_html('<span style="color: gray;">No reference</span>')

    casa_reference_display.short_description = "CASA Ref"

    def content_length(self, obj):
        """Display content length"""
        length = len(obj.content) if obj.content else 0
        if length > 1000:
            return format_html('<span style="color: green;">{} chars</span>', length)
        elif length > 100:
            return format_html('<span style="color: orange;">{} chars</span>', length)
        else:
            return format_html('<span style="color: gray;">{} chars</span>', length)

    content_length.short_description = "Content"


@admin.register(ManualApprovalHistory)
class ManualApprovalHistoryAdmin(admin.ModelAdmin):
    """Admin interface for Manual Approval History"""

    list_display = [
        "operations_manual",
        "action_display",
        "performed_by",
        "action_date",
        "version_at_action",
        "signature_status",
    ]

    list_filter = ["action", "action_date", "operations_manual__manual_type"]

    search_fields = [
        "operations_manual__manual_id",
        "operations_manual__title",
        "performed_by__username",
        "comments",
    ]

    readonly_fields = ["action_date", "ip_address"]

    fieldsets = (
        (
            "Action Details",
            {
                "fields": (
                    ("operations_manual", "action"),
                    ("performed_by", "action_date"),
                    "version_at_action",
                    "comments",
                )
            },
        ),
        (
            "Digital Signature",
            {"fields": ("digital_signature", "ip_address"), "classes": ("collapse",)},
        ),
    )

    def action_display(self, obj):
        """Display action with icon"""
        icons = {
            "created": "📝",
            "reviewed": "👀",
            "approved": "✅",
            "published": "📚",
            "revised": "🔄",
            "superseded": "⏏️",
            "withdrawn": "🚫",
        }
        icon = icons.get(obj.action, "📄")

        return format_html("{} {}", icon, obj.get_action_display())

    action_display.short_description = "Action"

    def signature_status(self, obj):
        """Display digital signature status"""
        if obj.digital_signature:
            return format_html('<span style="color: green;">✓ Signed</span>')
        return format_html('<span style="color: gray;">No signature</span>')

    signature_status.short_description = "Signature"


@admin.register(ManualDistributionRecord)
class ManualDistributionRecordAdmin(admin.ModelAdmin):
    """Admin interface for Manual Distribution Records"""

    list_display = [
        "operations_manual",
        "distributed_to",
        "version_distributed",
        "distribution_date",
        "acknowledgment_status",
        "access_status",
    ]

    list_filter = [
        "acknowledgment_required",
        "access_revoked",
        "distribution_date",
        "operations_manual__manual_type",
    ]

    search_fields = [
        "operations_manual__manual_id",
        "distributed_to__username",
        "distributed_to__first_name",
        "distributed_to__last_name",
    ]

    readonly_fields = ["distribution_date"]

    fieldsets = (
        (
            "Distribution Details",
            {
                "fields": (
                    ("operations_manual", "version_distributed"),
                    ("distributed_to", "access_granted_by"),
                    "distribution_date",
                )
            },
        ),
        (
            "Acknowledgment",
            {"fields": ("acknowledgment_required", "acknowledged_date")},
        ),
        ("Access Control", {"fields": ("access_revoked", "revocation_date")}),
    )

    def acknowledgment_status(self, obj):
        """Display acknowledgment status"""
        if not obj.acknowledgment_required:
            return format_html('<span style="color: gray;">Not required</span>')

        if obj.acknowledged_date:
            return format_html(
                '<span style="color: green;">✓ Acknowledged</span><br>'
                "<small>{}</small>",
                obj.acknowledged_date.strftime("%d/%m/%Y"),
            )
        elif obj.acknowledgment_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ OVERDUE</span>'
            )
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')

    acknowledgment_status.short_description = "Acknowledgment"

    def access_status(self, obj):
        """Display access status"""
        if obj.access_revoked:
            return format_html(
                '<span style="color: red;">🚫 Revoked</span><br>' "<small>{}</small>",
                (
                    obj.revocation_date.strftime("%d/%m/%Y")
                    if obj.revocation_date
                    else "Date unknown"
                ),
            )
        elif obj.is_current_access:
            return format_html('<span style="color: green;">✓ Active</span>')
        else:
            return format_html('<span style="color: orange;">⚠ Inactive</span>')

    access_status.short_description = "Access"
