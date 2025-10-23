from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    RPASOperationsManual,
    SOPProcedureStep,
    StandardOperatingProcedure,
    TrainingSyllabus,
)


class StandardOperatingProcedureForm(forms.ModelForm):
    """Form for creating and editing Standard Operating Procedures"""

    class Meta:
        model = StandardOperatingProcedure
        fields = [
            "sop_id",
            "title",
            "category",
            "version",
            "purpose",
            "scope",
            "responsibilities",
            "definitions",
            "references",
            "aircraft_types",
            "priority",
            "frequency_of_use",
            "status",
            "reviewed_by",
            "approved_by",
            "reviewed_date",
            "approved_date",
            "effective_date",
            "next_review_date",
            "supersedes",
        ]

        widgets = {
            "sop_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "XXX-XXX-SOP (e.g., FLT-001-SOP)",
                    "pattern": "^[A-Z]{3}-[0-9]{3}-SOP$",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter clear, descriptive SOP title",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "version": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., 1.0, 2.1",
                }
            ),
            "purpose": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Clearly state the objective of the procedure",
                }
            ),
            "scope": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Define the specific activities or aircraft the procedure applies to",
                }
            ),
            "responsibilities": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Outline who is responsible for carrying out each step",
                }
            ),
            "definitions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Define any technical terms or jargon used in the procedure",
                }
            ),
            "references": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "List any relevant regulations, manuals, or other documents",
                }
            ),
            "aircraft_types": forms.CheckboxSelectMultiple(
                attrs={"class": "form-check-input"}
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "frequency_of_use": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "reviewed_by": forms.Select(attrs={"class": "form-select"}),
            "approved_by": forms.Select(attrs={"class": "form-select"}),
            "reviewed_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "approved_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "effective_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "next_review_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "supersedes": forms.Select(attrs={"class": "form-select"}),
        }

        labels = {
            "sop_id": "SOP ID",
            "title": "SOP Title",
            "category": "SOP Category",
            "version": "Version",
            "purpose": "Purpose",
            "scope": "Scope",
            "responsibilities": "Responsibilities",
            "definitions": "Definitions",
            "references": "References",
            "aircraft_types": "Applicable Aircraft Types",
            "priority": "Priority Level",
            "frequency_of_use": "Frequency of Use",
            "status": "Approval Status",
            "reviewed_by": "Reviewed By",
            "approved_by": "Approved By",
            "reviewed_date": "Review Date",
            "approved_date": "Approval Date",
            "effective_date": "Effective Date",
            "next_review_date": "Next Review Date",
            "supersedes": "Supersedes SOP",
        }

        help_texts = {
            "sop_id": "Unique SOP identifier in format XXX-XXX-SOP (leave blank for auto-generation)",
            "title": "Clear, descriptive title of the procedure",
            "category": "CASA operational category for this SOP",
            "version": "Version number for tracking revisions",
            "purpose": "Clearly state the objective and reason for this procedure",
            "scope": "Define the specific activities, aircraft, or personnel this procedure applies to",
            "responsibilities": "Outline who is responsible for carrying out each step of the procedure",
            "definitions": "Define any technical terms, jargon, or acronyms used in the procedure",
            "references": "List relevant regulations, manuals, or documents referenced in this SOP",
            "aircraft_types": "Select aircraft types this SOP applies to (if applicable)",
            "priority": "Priority level for implementation and training",
            "frequency_of_use": "How often this procedure is expected to be used",
            "status": "Current approval and implementation status",
            "reviewed_by": "Staff member who reviewed this SOP",
            "approved_by": "Authority who approved this SOP for implementation",
            "reviewed_date": "Date when SOP was last reviewed",
            "approved_date": "Date when SOP was approved",
            "effective_date": "Date when SOP becomes effective",
            "next_review_date": "Date when SOP should be next reviewed",
            "supersedes": "Previous SOP that this SOP replaces (if applicable)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make staff profile querysets more efficient
        from accounts.models import StaffProfile

        staff_queryset = StaffProfile.objects.select_related("user").order_by(
            "user__first_name"
        )

        self.fields["reviewed_by"].queryset = staff_queryset
        self.fields["approved_by"].queryset = staff_queryset

        # Make supersedes queryset exclude current instance
        supersedes_queryset = StandardOperatingProcedure.objects.exclude(
            pk=self.instance.pk if self.instance.pk else None
        ).order_by("sop_id")
        self.fields["supersedes"].queryset = supersedes_queryset

        # Make SOP ID optional for auto-generation
        self.fields["sop_id"].required = False

    def clean_sop_id(self):
        """Validate SOP ID format and uniqueness"""
        sop_id = self.cleaned_data.get("sop_id", "").strip().upper()

        if sop_id:
            # Validate format
            import re

            if not re.match(r"^[A-Z]{3}-\d{3}-SOP$", sop_id):
                raise ValidationError(
                    "SOP ID must be in format XXX-XXX-SOP (e.g., FLT-001-SOP)."
                )

            # Check uniqueness (exclude current instance if updating)
            queryset = StandardOperatingProcedure.objects.filter(sop_id=sop_id)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise ValidationError("This SOP ID is already in use.")

        return sop_id

    def clean_effective_date(self):
        """Validate effective date"""
        effective_date = self.cleaned_data.get("effective_date")

        if (
            effective_date
            and effective_date < timezone.now().date()
            and not self.instance.pk
        ):
            raise ValidationError("Effective date cannot be in the past for new SOPs.")

        return effective_date

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        approved_by = cleaned_data.get("approved_by")
        approved_date = cleaned_data.get("approved_date")
        effective_date = cleaned_data.get("effective_date")

        # Approved SOPs must have approval details
        if status == "approved":
            if not all([approved_by, approved_date, effective_date]):
                raise ValidationError(
                    "Approved SOPs must have approved_by, approved_date, and effective_date."
                )

        # Review date validation
        reviewed_date = cleaned_data.get("reviewed_date")
        next_review_date = cleaned_data.get("next_review_date")

        if (
            reviewed_date
            and next_review_date
            and reviewed_date.date() >= next_review_date
        ):
            raise ValidationError("Next review date must be after the review date.")

        return cleaned_data


class SOPProcedureStepForm(forms.ModelForm):
    """Form for creating and editing SOP procedure steps"""

    class Meta:
        model = SOPProcedureStep
        fields = [
            "step_number",
            "step_type",
            "title",
            "description",
            "responsible_role",
            "duration_estimate",
            "safety_critical",
            "verification_required",
            "notes",
            "prerequisite_steps",
        ]

        widgets = {
            "step_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "step_type": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Brief title describing this step",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Detailed description of the step to be performed",
                }
            ),
            "responsible_role": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Pilot, Maintenance Tech, Safety Officer",
                }
            ),
            "duration_estimate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "Estimated minutes",
                }
            ),
            "safety_critical": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "verification_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional notes, warnings, or references",
                }
            ),
            "prerequisite_steps": forms.CheckboxSelectMultiple(),
        }

        labels = {
            "step_number": "Step Number",
            "step_type": "Step Type",
            "title": "Step Title",
            "description": "Step Description",
            "responsible_role": "Responsible Role",
            "duration_estimate": "Duration Estimate (minutes)",
            "safety_critical": "Safety Critical",
            "verification_required": "Verification Required",
            "notes": "Additional Notes",
            "prerequisite_steps": "Prerequisite Steps",
        }

        help_texts = {
            "step_number": "Sequential step number within the procedure",
            "step_type": "Type of procedural step",
            "title": "Brief title describing this step",
            "description": "Detailed description of the step to be performed",
            "responsible_role": "Role or position responsible for this step",
            "duration_estimate": "Estimated time to complete this step in minutes",
            "safety_critical": "Check if this step is safety critical",
            "verification_required": "Check if this step requires verification/sign-off",
            "notes": "Additional notes, warnings, or references for this step",
            "prerequisite_steps": "Steps that must be completed before this step",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If this is for a specific SOP, limit prerequisite steps to same SOP
        if hasattr(self.instance, 'sop') and self.instance.sop:
            self.fields["prerequisite_steps"].queryset = (
                SOPProcedureStep.objects.filter(sop=self.instance.sop).exclude(
                    pk=self.instance.pk if self.instance.pk else None
                )
            )

    def clean_step_number(self):
        """Validate step number"""
        step_number = self.cleaned_data.get("step_number")

        if step_number and step_number < 1:
            raise ValidationError("Step number must be positive.")

        return step_number


class TrainingSyllabusForm(forms.ModelForm):
    """Form for creating and editing Training Syllabuses"""

    class Meta:
        model = TrainingSyllabus
        fields = [
            "syllabus_id",
            "title",
            "category",
            "training_type",
            "applicability",
            "description",
            "learning_objectives",
            "prerequisites",
            "duration_hours",
            "theory_hours",
            "practical_hours",
            "assessment_method",
            "pass_mark",
            "competency_standards",
            "casa_reference",
            "regulatory_requirement",
            "validity_period_months",
            "recurrent_training_required",
            "aircraft_types",
            "status",
            "approved_by",
            "approved_date",
        ]

        widgets = {
            "syllabus_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., G1.1, G2.1, G3.1",
                    "pattern": "^[A-Z]\\d+(\\.\\d+)*$",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter training syllabus title",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "training_type": forms.Select(attrs={"class": "form-select"}),
            "applicability": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Detailed description of the training program",
                }
            ),
            "learning_objectives": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Specific learning objectives to be achieved",
                }
            ),
            "prerequisites": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Prerequisites for this training",
                }
            ),
            "duration_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.5",
                }
            ),
            "theory_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.5",
                }
            ),
            "practical_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.5",
                }
            ),
            "assessment_method": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Written test, Practical demonstration",
                }
            ),
            "pass_mark": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "100",
                }
            ),
            "competency_standards": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Performance criteria and standards for competency",
                }
            ),
            "casa_reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CASA regulation reference",
                }
            ),
            "regulatory_requirement": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "validity_period_months": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "recurrent_training_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "aircraft_types": forms.CheckboxSelectMultiple(
                attrs={"class": "form-check-input"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "approved_by": forms.Select(attrs={"class": "form-select"}),
            "approved_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make staff profile queryset more efficient
        from accounts.models import StaffProfile

        staff_queryset = StaffProfile.objects.select_related("user").order_by(
            "user__first_name"
        )
        self.fields["approved_by"].queryset = staff_queryset

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()

        practical_hours = cleaned_data.get("practical_hours", 0) or 0
        theory_hours = cleaned_data.get("theory_hours", 0) or 0
        total_duration = cleaned_data.get("duration_hours", 0) or 0

        if practical_hours + theory_hours > total_duration:
            raise ValidationError(
                "Combined practical and theory hours cannot exceed total training duration."
            )

        # Approval validation
        status = cleaned_data.get("status")
        approved_by = cleaned_data.get("approved_by")
        approved_date = cleaned_data.get("approved_date")

        if status == "approved" and not all([approved_by, approved_date]):
            raise ValidationError(
                "Approved syllabuses must have approved_by and approved_date."
            )

        return cleaned_data


class RPASOperationsManualForm(forms.ModelForm):
    """Form for creating and editing RPAS Operations Manuals"""

    class Meta:
        model = RPASOperationsManual
        fields = [
            "manual_id",
            "title",
            "manual_type",
            "version",
            "revision_number",
            "effective_date",
            "next_review_date",
            "status",
            "casa_approved",
            "casa_approval_reference",
            "casa_approval_date",
            "organization_name",
            "reoc_number",
            "prepared_by",
            "reviewed_by",
            "approved_by",
            "approval_date",
            "purpose",
            "abstract",
            "applicable_regulations",
            "change_summary",
            "supersedes_version",
            "controlled_distribution",
            "digital_signature_required",
            "related_sops",
            "training_syllabus",
        ]

        widgets = {
            "manual_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., OPS-2025-001, MNT-2025-001",
                    "pattern": "^(OPS|MNT|TRN|EMG|SMS|QUA)-\\d{4}-\\d{3}$",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter manual title",
                }
            ),
            "manual_type": forms.Select(attrs={"class": "form-select"}),
            "version": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., 1.0, 2.1",
                }
            ),
            "revision_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
            "effective_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "next_review_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "casa_approved": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "casa_approval_reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CASA approval reference number",
                }
            ),
            "casa_approval_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "organization_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Organization name",
                }
            ),
            "reoc_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Remote Operator Certificate number",
                }
            ),
            "prepared_by": forms.Select(attrs={"class": "form-select"}),
            "reviewed_by": forms.Select(attrs={"class": "form-select"}),
            "approved_by": forms.Select(attrs={"class": "form-select"}),
            "approval_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "purpose": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Purpose and scope of this manual",
                }
            ),
            "abstract": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Brief summary of manual contents",
                }
            ),
            "applicable_regulations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                }
            ),
            "change_summary": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Summary of changes from previous version",
                }
            ),
            "supersedes_version": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., 1.0",
                }
            ),
            "controlled_distribution": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "digital_signature_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "related_sops": forms.CheckboxSelectMultiple(),
            "training_syllabus": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make querysets more efficient
        from accounts.models import CustomUser, KeyPersonnel

        user_queryset = CustomUser.objects.order_by("first_name", "last_name")
        self.fields["prepared_by"].queryset = user_queryset
        self.fields["reviewed_by"].queryset = user_queryset

        personnel_queryset = KeyPersonnel.objects.select_related("user").order_by(
            "user__first_name"
        )
        self.fields["approved_by"].queryset = personnel_queryset

    def clean_manual_id(self):
        """Validate manual ID uniqueness"""
        manual_id = self.cleaned_data.get("manual_id", "").strip().upper()

        if not manual_id:
            raise ValidationError("Manual ID is required.")

        # Check uniqueness (exclude current instance if updating)
        queryset = RPASOperationsManual.objects.filter(manual_id=manual_id)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError("This Manual ID is already in use.")

        return manual_id

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()

        # Date validation
        approval_date = cleaned_data.get("approval_date")
        effective_date = cleaned_data.get("effective_date")
        next_review_date = cleaned_data.get("next_review_date")
        casa_approval_date = cleaned_data.get("casa_approval_date")

        if approval_date and effective_date and approval_date > effective_date:
            raise ValidationError("Effective date cannot be before approval date.")

        if effective_date and next_review_date and effective_date >= next_review_date:
            raise ValidationError("Next review date must be after effective date.")

        # CASA approval validation
        casa_approved = cleaned_data.get("casa_approved")
        if casa_approved and not casa_approval_date:
            raise ValidationError(
                "CASA approval date is required when manual is CASA approved."
            )

        return cleaned_data
