from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class StandardOperatingProcedure(models.Model):
    """
    CASA-compliant Standard Operating Procedure (SOP) Model
    Follows CASA regulatory requirements for documented procedures
    """

    # SOP Categories aligned with CASA requirements
    CATEGORY_CHOICES = [
        ("flight_ops", "Flight Operations"),
        ("maintenance", "Maintenance Operations"),
        ("safety", "Safety Procedures"),
        ("emergency", "Emergency Procedures"),
        ("training", "Training Procedures"),
        ("security", "Security Procedures"),
        ("ground_ops", "Ground Operations"),
        ("weather", "Weather Procedures"),
        ("navigation", "Navigation Procedures"),
        ("communication", "Communication Procedures"),
    ]

    # Approval Status
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("review", "Under Review"),
        ("approved", "Approved"),
        ("revision", "Requires Revision"),
        ("superseded", "Superseded"),
        ("withdrawn", "Withdrawn"),
    ]

    # Priority Level
    PRIORITY_CHOICES = [
        ("critical", "Critical - Safety Critical"),
        ("high", "High Priority"),
        ("medium", "Medium Priority"),
        ("low", "Low Priority"),
    ]

    # SOP Identification
    sop_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="SOP ID",
        help_text="Format: XXX-XXX-SOP (e.g., FLT-001-SOP)",
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{3}-\d{3}-SOP$",
                message="Format must be XXX-XXX-SOP (e.g., FLT-001-SOP)",
            )
        ],
    )

    title = models.CharField(
        max_length=200,
        verbose_name="SOP Title",
        help_text="Clear, descriptive title of the procedure",
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="SOP Category",
        help_text="CASA operational category",
    )

    version = models.CharField(
        max_length=10,
        default="1.0",
        verbose_name="Version",
        help_text="Version number (e.g., 1.0, 2.1)",
    )

    # CASA Compliance Fields
    purpose = models.TextField(
        verbose_name="Purpose", help_text="Clearly state the objective of the procedure"
    )

    scope = models.TextField(
        verbose_name="Scope",
        help_text="Define the specific activities or aircraft the procedure applies to",
    )

    responsibilities = models.TextField(
        verbose_name="Responsibilities",
        help_text="Outline who is responsible for carrying out each step",
    )

    definitions = models.TextField(
        blank=True,
        verbose_name="Definitions",
        help_text="Define any technical terms or jargon used in the procedure",
    )

    references = models.TextField(
        blank=True,
        verbose_name="References",
        help_text="List any relevant regulations, manuals, or other documents",
    )

    # Operational Details
    aircraft_types = models.ManyToManyField(
        "aircraft.AircraftType",
        blank=True,
        verbose_name="Applicable Aircraft Types",
        help_text="Aircraft types this SOP applies to",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="Priority Level",
    )

    frequency_of_use = models.CharField(
        max_length=20,
        choices=[
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("as_required", "As Required"),
            ("emergency_only", "Emergency Only"),
        ],
        default="as_required",
        verbose_name="Frequency of Use",
    )

    # Review and Approval
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Approval Status",
    )

    created_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="created_sops",
        verbose_name="Created By",
        help_text="Staff member who created this SOP",
    )

    reviewed_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="reviewed_sops",
        null=True,
        blank=True,
        verbose_name="Reviewed By",
        help_text="Staff member who reviewed this SOP",
    )

    approved_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="approved_sops",
        null=True,
        blank=True,
        verbose_name="Approved By",
        help_text="Authority who approved this SOP",
    )

    # Important Dates
    created_date = models.DateTimeField(auto_now_add=True)
    reviewed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Review Date",
        help_text="Date when SOP was last reviewed",
    )

    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Approval Date",
        help_text="Date when SOP was approved",
    )

    effective_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Effective Date",
        help_text="Date when SOP becomes effective",
    )

    next_review_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Next Review Date",
        help_text="Date when SOP should be next reviewed",
    )

    # Superseded Information
    superseded_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Superseded By",
        help_text="SOP that replaces this one",
    )

    supersedes = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="superseded_sops",
        verbose_name="Supersedes",
        help_text="SOP that this one replaces",
    )

    # Metadata
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Standard Operating Procedure"
        verbose_name_plural = "Standard Operating Procedures"
        ordering = ["category", "sop_id"]

    def __str__(self):
        return f"{self.sop_id} - {self.title}"

    def clean(self):
        """Validate SOP data"""
        # Approved SOPs must have approval details
        if self.status == "approved":
            if not all([self.approved_by, self.approved_date, self.effective_date]):
                raise ValidationError(
                    "Approved SOPs must have approved_by, approved_date, and effective_date"
                )

        # Effective date cannot be in the past for new SOPs
        if (
            self.effective_date
            and self.effective_date < timezone.now().date()
            and not self.pk
        ):
            raise ValidationError("Effective date cannot be in the past for new SOPs")

    def save(self, *args, **kwargs):
        """Auto-generate SOP ID if not provided"""
        if not self.sop_id:
            # Generate SOP ID based on category
            category_prefixes = {
                "flight_ops": "FLT",
                "maintenance": "MNT",
                "safety": "SAF",
                "emergency": "EMG",
                "training": "TRN",
                "security": "SEC",
                "ground_ops": "GND",
                "weather": "WTH",
                "navigation": "NAV",
                "communication": "COM",
            }

            prefix = category_prefixes.get(self.category, "GEN")

            # Get next sequence number for this category
            last_sop = (
                StandardOperatingProcedure.objects.filter(
                    sop_id__startswith=f"{prefix}-"
                )
                .order_by("sop_id")
                .last()
            )

            if last_sop:
                last_seq = int(last_sop.sop_id.split("-")[1])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.sop_id = f"{prefix}-{next_seq:03d}-SOP"

        super().save(*args, **kwargs)

    @property
    def is_current(self):
        """Check if SOP is current and not superseded"""
        return self.status == "approved" and not self.superseded_by

    @property
    def is_overdue_review(self):
        """Check if SOP is overdue for review"""
        if self.next_review_date:
            return self.next_review_date < timezone.now().date()
        return False

    @property
    def procedure_steps_count(self):
        """Get count of procedure steps"""
        return self.procedure_steps.count()

    @property
    def has_risk_assessment(self):
        """Check if SOP has associated risk assessment"""
        return self.risk_assessments.exists()


class SOPProcedureStep(models.Model):
    """
    Individual steps within a Standard Operating Procedure
    Allows for detailed step-by-step documentation
    """

    STEP_TYPE_CHOICES = [
        ("normal", "Normal Operation"),
        ("emergency", "Emergency Procedure"),
        ("contingency", "Contingency Procedure"),
        ("safety_check", "Safety Check"),
        ("verification", "Verification Step"),
    ]

    sop = models.ForeignKey(
        StandardOperatingProcedure,
        on_delete=models.CASCADE,
        related_name="procedure_steps",
        verbose_name="SOP",
    )

    step_number = models.PositiveIntegerField(
        verbose_name="Step Number",
        help_text="Sequential step number within the procedure",
    )

    step_type = models.CharField(
        max_length=15,
        choices=STEP_TYPE_CHOICES,
        default="normal",
        verbose_name="Step Type",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Step Title",
        help_text="Brief title describing this step",
    )

    description = models.TextField(
        verbose_name="Step Description",
        help_text="Detailed description of the step to be performed",
    )

    responsible_role = models.CharField(
        max_length=100,
        verbose_name="Responsible Role",
        help_text="Role or position responsible for this step (e.g., Pilot, Maintenance Tech)",
    )

    duration_estimate = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Duration (minutes)",
        help_text="Estimated time to complete this step",
    )

    safety_critical = models.BooleanField(
        default=False,
        verbose_name="Safety Critical",
        help_text="Mark if this step is safety critical",
    )

    verification_required = models.BooleanField(
        default=False,
        verbose_name="Verification Required",
        help_text="Mark if this step requires verification/sign-off",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Additional Notes",
        help_text="Additional notes, warnings, or references for this step",
    )

    # Dependencies
    prerequisite_steps = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        verbose_name="Prerequisite Steps",
        help_text="Steps that must be completed before this step",
    )

    class Meta:
        verbose_name = "SOP Procedure Step"
        verbose_name_plural = "SOP Procedure Steps"
        ordering = ["sop", "step_number"]
        unique_together = ["sop", "step_number"]

    def __str__(self):
        return f"{self.sop.sop_id} - Step {self.step_number}: {self.title}"


class SOPRiskAssessment(models.Model):
    """
    Risk Assessment for Standard Operating Procedures
    Links SOPs to the risk assessment framework in flight_operations
    """

    sop = models.ForeignKey(
        StandardOperatingProcedure,
        on_delete=models.CASCADE,
        related_name="risk_assessments",
        verbose_name="SOP",
    )

    # Link to flight operations risk register
    risk_register = models.ForeignKey(
        "flight_operations.RiskRegister",
        on_delete=models.CASCADE,
        verbose_name="Risk Register Entry",
        help_text="Associated risk register entry from flight operations",
    )

    # SOP-specific risk information
    risk_context = models.TextField(
        verbose_name="Risk Context in SOP",
        help_text="How this risk applies specifically to this SOP",
    )

    mitigation_steps = models.ManyToManyField(
        SOPProcedureStep,
        blank=True,
        verbose_name="Mitigation Steps",
        help_text="Specific SOP steps that mitigate this risk",
    )

    monitoring_requirements = models.TextField(
        blank=True,
        verbose_name="Monitoring Requirements",
        help_text="How this risk should be monitored during SOP execution",
    )

    # Risk ownership for this SOP context
    risk_owner = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        verbose_name="Risk Owner for SOP",
        help_text="Person responsible for managing this risk in SOP context",
    )

    # Assessment dates
    assessed_date = models.DateTimeField(auto_now_add=True)
    last_reviewed = models.DateTimeField(auto_now=True)
    next_review_date = models.DateField(
        verbose_name="Next Review Date",
        help_text="When this risk assessment should be next reviewed",
    )

    class Meta:
        verbose_name = "SOP Risk Assessment"
        verbose_name_plural = "SOP Risk Assessments"
        unique_together = ["sop", "risk_register"]

    def __str__(self):
        return f"{self.sop.sop_id} - {self.risk_register.hazard[:50]}"


class TrainingSyllabus(models.Model):
    """
    CASA-compliant Training Syllabus Model
    Based on CASA training requirements and industry standards
    """

    # Training Categories based on CASA requirements
    TRAINING_CATEGORY_CHOICES = [
        ("G1", "G1 - Policy and Procedure Training"),
        ("G2", "G2 - RPAS Type Training"),
        ("G3", "G3 - Night Visual Line of Sight Training"),
        ("maintenance", "Maintenance Training"),
        ("safety", "Safety Training"),
        ("emergency", "Emergency Procedures Training"),
        ("recurrent", "Recurrent Training"),
        ("proficiency", "Proficiency Check"),
        ("endorsement", "Endorsement Training"),
    ]

    # Training Types
    TRAINING_TYPE_CHOICES = [
        ("ground_theory", "Ground/Theory"),
        ("flight_exercises", "Flight Exercises"),
        ("practical_assessment", "Practical Assessment"),
        ("theory_test", "Theory Test"),
        ("competency_check", "Competency Check"),
        ("endorsement_check", "Endorsement Check"),
    ]

    # Applicability
    APPLICABILITY_CHOICES = [
        ("all_rps", "All RPs and Operational Crew Members"),
        ("rps_operating_rpa", "RPs Operating RPA Type (All Items)"),
        ("operational_crew", "Operational Crew Members (Role Relevant)"),
        ("rps_night_ops", "RPs Operating at Night"),
        ("maintenance_staff", "Maintenance Personnel"),
        ("safety_officers", "Safety Officers"),
    ]

    # Status
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("current", "Current"),
        ("superseded", "Superseded"),
        ("withdrawn", "Withdrawn"),
    ]

    # Syllabus Identification
    syllabus_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Syllabus ID",
        help_text="Format: G1.1, G2.1, G3.1, etc.",
        validators=[
            RegexValidator(
                regex=r"^[A-Z]\d+(\.\d+)*$", message="Format must be G1.1, G2.1, etc."
            )
        ],
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Training Title",
        help_text="Descriptive title of the training syllabus",
    )

    category = models.CharField(
        max_length=20,
        choices=TRAINING_CATEGORY_CHOICES,
        verbose_name="Training Category",
    )

    training_type = models.CharField(
        max_length=20, choices=TRAINING_TYPE_CHOICES, verbose_name="Training Type"
    )

    applicability = models.CharField(
        max_length=30,
        choices=APPLICABILITY_CHOICES,
        verbose_name="Applicability",
        help_text="Who this training applies to",
    )

    # Training Content
    description = models.TextField(
        verbose_name="Training Description",
        help_text="Detailed description of training content and objectives",
    )

    learning_objectives = models.TextField(
        verbose_name="Learning Objectives",
        help_text="Specific learning objectives and outcomes",
    )

    prerequisites = models.TextField(
        blank=True,
        verbose_name="Prerequisites",
        help_text="Required prior training or qualifications",
    )

    # Delivery Information
    duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Duration (Hours)",
        help_text="Total training duration in hours",
    )

    theory_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Theory Hours",
        help_text="Theory/ground school hours",
    )

    practical_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Practical Hours",
        help_text="Practical/flight training hours",
    )

    # Assessment Requirements
    assessment_method = models.CharField(
        max_length=100,
        verbose_name="Assessment Method",
        help_text="How competency is assessed (written test, practical, etc.)",
    )

    pass_mark = models.PositiveIntegerField(
        default=80,
        verbose_name="Pass Mark (%)",
        help_text="Minimum percentage required to pass",
    )

    competency_standards = models.TextField(
        verbose_name="Competency Standards",
        help_text="Performance criteria and standards for competency",
    )

    # CASA Compliance
    casa_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="CASA Reference",
        help_text="CASA regulation or manual reference",
    )

    regulatory_requirement = models.BooleanField(
        default=True,
        verbose_name="Regulatory Requirement",
        help_text="Is this training mandatory under CASA regulations?",
    )

    # Validity and Recurrency
    validity_period_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Validity Period (Months)",
        help_text="How long this training remains valid",
    )

    recurrent_training_required = models.BooleanField(
        default=False,
        verbose_name="Recurrent Training Required",
        help_text="Does this training require periodic renewal?",
    )

    # Applicable Aircraft Types
    aircraft_types = models.ManyToManyField(
        "aircraft.AircraftType",
        blank=True,
        verbose_name="Applicable Aircraft Types",
        help_text="Aircraft types this training applies to",
    )

    # Approval and Status
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="draft", verbose_name="Status"
    )

    approved_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="approved_syllabi",
        null=True,
        blank=True,
        verbose_name="Approved By",
        help_text="Authority who approved this training syllabus",
    )

    approved_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Approval Date"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="created_syllabi",
        verbose_name="Created By",
    )

    class Meta:
        verbose_name = "Training Syllabus"
        verbose_name_plural = "Training Syllabi"
        ordering = ["category", "syllabus_id"]

    def __str__(self):
        return f"{self.syllabus_id} - {self.title}"

    def clean(self):
        """Validate training syllabus data"""
        # Theory + Practical should not exceed total duration
        if self.theory_hours + self.practical_hours > self.duration_hours:
            raise ValidationError(
                "Theory hours + Practical hours cannot exceed total duration"
            )

        # Approved syllabi must have approval details
        if self.status == "approved" and not all(
            [self.approved_by, self.approved_date]
        ):
            raise ValidationError(
                "Approved syllabi must have approved_by and approved_date"
            )

    @property
    def is_current(self):
        """Check if syllabus is current"""
        return self.status in ["approved", "current"]

    @property
    def training_records_count(self):
        """Get count of training records using this syllabus"""
        return self.training_records.count()


class TrainingRegister(models.Model):
    """
    Training Register Model
    Tracks all pilot and staff training requirements and completions
    Industry standard compliance tracking
    """

    # Training Status
    STATUS_CHOICES = [
        ("required", "Required"),
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed - Requires Retrain"),
        ("expired", "Expired"),
        ("waived", "Waived"),
    ]

    # Training Priority
    PRIORITY_CHOICES = [
        ("critical", "Critical - Immediate"),
        ("high", "High Priority"),
        ("medium", "Medium Priority"),
        ("low", "Low Priority"),
    ]

    # Record Identification
    training_record_id = models.CharField(
        max_length=25,
        unique=True,
        verbose_name="Training Record ID",
        help_text="Format: TR-YYYY-XXXXXX",
        validators=[
            RegexValidator(
                regex=r"^TR-\d{4}-\d{6}$", message="Format must be TR-YYYY-XXXXXX"
            )
        ],
    )

    # Personnel (using Generic Foreign Key for Pilot or Staff)
    trainee_pilot = models.ForeignKey(
        "accounts.PilotProfile",
        on_delete=models.CASCADE,
        related_name="training_records",
        null=True,
        blank=True,
        verbose_name="Trainee (Pilot)",
        help_text="Pilot receiving training",
    )

    trainee_staff = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.CASCADE,
        related_name="training_records",
        null=True,
        blank=True,
        verbose_name="Trainee (Staff)",
        help_text="Staff member receiving training",
    )

    # Training Details
    training_syllabus = models.ForeignKey(
        TrainingSyllabus,
        on_delete=models.PROTECT,
        related_name="training_records",
        verbose_name="Training Syllabus",
    )

    # Scheduling
    required_by_date = models.DateField(
        verbose_name="Required By Date",
        help_text="Date by which training must be completed",
    )

    scheduled_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Scheduled Date/Time",
        help_text="When training is scheduled to occur",
    )

    # Completion Details
    started_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Training Started",
        help_text="When training commenced",
    )

    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Training Completed",
        help_text="When training was successfully completed",
    )

    # Assessment Results
    assessment_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Assessment Score (%)",
        help_text="Assessment score as percentage",
    )

    passed = models.BooleanField(
        default=False,
        verbose_name="Passed Assessment",
        help_text="Did trainee pass the assessment?",
    )

    # Training Delivery
    instructor = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="instructed_training",
        null=True,
        blank=True,
        verbose_name="Instructor",
        help_text="Instructor who delivered the training",
    )

    training_provider = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Training Provider",
        help_text="External training provider (if applicable)",
    )

    training_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Training Location",
        help_text="Where training was conducted",
    )

    # Documentation
    certificate_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Certificate Number",
        help_text="Training certificate or endorsement number",
    )

    training_notes = models.TextField(
        blank=True,
        verbose_name="Training Notes",
        help_text="Additional notes about training delivery or performance",
    )

    # Status and Priority
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="required",
        verbose_name="Training Status",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="Priority Level",
    )

    # Validity Tracking
    valid_from = models.DateField(
        null=True,
        blank=True,
        verbose_name="Valid From",
        help_text="Date from which training certification is valid",
    )

    valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Valid Until",
        help_text="Date when training certification expires",
    )

    # Recurrent Training
    next_recurrent_due = models.DateField(
        null=True,
        blank=True,
        verbose_name="Next Recurrent Due",
        help_text="When recurrent training is next due",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="created_training_records",
        verbose_name="Created By",
    )

    class Meta:
        verbose_name = "Training Register"
        verbose_name_plural = "Training Register"
        ordering = ["-required_by_date", "-created_at"]

    def __str__(self):
        trainee_name = self.get_trainee_name()
        return f"{self.training_record_id} - {trainee_name} - {self.training_syllabus.title}"

    def clean(self):
        """Validate training register data"""
        # Must have either pilot or staff trainee, but not both
        if not (self.trainee_pilot or self.trainee_staff):
            raise ValidationError("Must specify either pilot or staff trainee")

        if self.trainee_pilot and self.trainee_staff:
            raise ValidationError("Cannot specify both pilot and staff trainee")

        # Completed training must have completion date and pass status
        if self.status == "completed":
            if not self.completed_date:
                raise ValidationError("Completed training must have completion date")
            if not self.passed:
                raise ValidationError("Completed training must be marked as passed")

        # Failed training cannot be marked as passed
        if self.status == "failed" and self.passed:
            raise ValidationError("Failed training cannot be marked as passed")

        # Assessment score validation
        if self.assessment_score is not None:
            if self.assessment_score < 0 or self.assessment_score > 100:
                raise ValidationError("Assessment score must be between 0 and 100")

    def save(self, *args, **kwargs):
        """Auto-generate training record ID and set validity dates"""
        if not self.training_record_id:
            year = timezone.now().year
            last_record = (
                TrainingRegister.objects.filter(
                    training_record_id__startswith=f"TR-{year}-"
                )
                .order_by("training_record_id")
                .last()
            )

            if last_record:
                last_seq = int(last_record.training_record_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.training_record_id = f"TR-{year}-{next_seq:06d}"

        # Auto-set validity dates based on completion
        if self.status == "completed" and self.completed_date:
            self.valid_from = self.completed_date.date()

            # Set expiry based on syllabus validity period
            if self.training_syllabus.validity_period_months:
                from dateutil.relativedelta import relativedelta

                self.valid_until = self.valid_from + relativedelta(
                    months=self.training_syllabus.validity_period_months
                )

            # Set next recurrent training if required
            if self.training_syllabus.recurrent_training_required and self.valid_until:
                # Schedule recurrent training 30 days before expiry
                from datetime import timedelta

                self.next_recurrent_due = self.valid_until - timedelta(days=30)

        super().save(*args, **kwargs)

    def get_trainee_name(self):
        """Get the name of the trainee"""
        if self.trainee_pilot:
            return self.trainee_pilot.user.get_full_name()
        elif self.trainee_staff:
            return self.trainee_staff.user.get_full_name()
        return "Unknown Trainee"

    def get_trainee_profile(self):
        """Get the trainee profile"""
        return self.trainee_pilot or self.trainee_staff

    @property
    def is_overdue(self):
        """Check if training is overdue"""
        if self.status in ["completed"]:
            return False
        return self.required_by_date < timezone.now().date()

    @property
    def is_expired(self):
        """Check if training certification is expired"""
        if self.valid_until:
            return self.valid_until < timezone.now().date()
        return False

    @property
    def days_until_due(self):
        """Calculate days until training is due"""
        if self.status == "completed":
            return None

        delta = self.required_by_date - timezone.now().date()
        return delta.days

    @property
    def training_duration_actual(self):
        """Calculate actual training duration"""
        if self.started_date and self.completed_date:
            duration = self.completed_date - self.started_date
            return round(duration.total_seconds() / 3600, 2)  # Hours
        return None


class RPASOperationsManual(models.Model):
    """
    Digital RPAS Operations Manual - CASA Part 101 Compliance
    Comprehensive document management system for aviation operations
    Integrates with all operational procedures and regulatory requirements
    """

    # Document Status Choices
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("review", "Under Review"),
        ("approved", "Approved"),
        ("published", "Published"),
        ("superseded", "Superseded"),
        ("withdrawn", "Withdrawn"),
    ]

    # Manual Types
    MANUAL_TYPE_CHOICES = [
        ("operations", "Operations Manual"),
        ("maintenance", "Maintenance Manual"),
        ("training", "Training Manual"),
        ("emergency", "Emergency Procedures Manual"),
        ("safety", "Safety Management System Manual"),
        ("quality", "Quality Assurance Manual"),
    ]

    # Document Control
    manual_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Manual ID",
        help_text="Format: OPS-YYYY-XXX (e.g., OPS-2025-001)",
        validators=[
            RegexValidator(
                regex=r"^(OPS|MNT|TRN|EMG|SMS|QUA)-\d{4}-\d{3}$",
                message="Format: XXX-YYYY-XXX",
            )
        ],
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Manual Title",
        help_text="Complete title of operations manual",
    )

    manual_type = models.CharField(
        max_length=20,
        choices=MANUAL_TYPE_CHOICES,
        verbose_name="Manual Type",
        help_text="Type of operations manual",
    )

    # Version Control
    version = models.CharField(
        max_length=10,
        verbose_name="Version",
        help_text="Version number (e.g., 1.0, 2.1)",
    )

    revision_number = models.PositiveIntegerField(
        default=0,
        verbose_name="Revision Number",
        help_text="Sequential revision number",
    )

    effective_date = models.DateField(
        verbose_name="Effective Date", help_text="Date manual becomes effective"
    )

    next_review_date = models.DateField(
        verbose_name="Next Review Date",
        help_text="Required review date - typically annual",
    )

    # Document Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Document Status",
    )

    # CASA Compliance
    casa_approved = models.BooleanField(
        default=False, verbose_name="CASA Approved", help_text="Manual approved by CASA"
    )

    casa_approval_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="CASA Approval Reference",
        help_text="CASA approval or acceptance reference number",
    )

    casa_approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="CASA Approval Date",
        help_text="Date of CASA approval",
    )

    # Organizational Details
    organization_name = models.CharField(
        max_length=200,
        default="Drone Ultra Images",
        verbose_name="Organization Name",
        help_text="Operating organization name",
    )

    reoc_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="ReOC Number",
        help_text="Remote Operator Certificate number if applicable",
    )

    # Approval Chain
    prepared_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.PROTECT,
        related_name="manuals_prepared",
        verbose_name="Prepared By",
        help_text="Person who prepared the manual",
    )

    reviewed_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.PROTECT,
        related_name="manuals_reviewed",
        null=True,
        blank=True,
        verbose_name="Reviewed By",
        help_text="Person who reviewed the manual",
    )

    approved_by = models.ForeignKey(
        "accounts.KeyPersonnel",
        on_delete=models.PROTECT,
        related_name="manuals_approved",
        null=True,
        blank=True,
        verbose_name="Approved By",
        help_text="Key personnel who approved manual (typically CRP or Head of Operations)",
    )

    approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Approval Date",
        help_text="Date of organizational approval",
    )

    # Document Abstract
    purpose = models.TextField(
        verbose_name="Purpose and Scope",
        help_text="Purpose of manual and operational scope",
    )

    abstract = models.TextField(
        verbose_name="Abstract",
        help_text="Brief summary of manual contents and applicability",
    )

    # Regulatory References
    applicable_regulations = models.TextField(
        verbose_name="Applicable Regulations",
        default="CASA Part 101 - Unmanned Aircraft and Rocket Operations",
        help_text="Primary regulatory framework",
    )

    # Change Management
    change_summary = models.TextField(
        blank=True,
        verbose_name="Change Summary",
        help_text="Summary of changes from previous version",
    )

    supersedes_version = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Supersedes Version",
        help_text="Previous version that this manual supersedes",
    )

    # Distribution Control
    controlled_distribution = models.BooleanField(
        default=True,
        verbose_name="Controlled Distribution",
        help_text="Manual requires controlled distribution",
    )

    digital_signature_required = models.BooleanField(
        default=True,
        verbose_name="Digital Signature Required",
        help_text="Requires digital signatures for approval",
    )

    # Integration References
    related_sops = models.ManyToManyField(
        StandardOperatingProcedure,
        blank=True,
        verbose_name="Related SOPs",
        help_text="SOPs incorporated or referenced in this manual",
    )

    training_syllabus = models.ManyToManyField(
        TrainingSyllabus,
        blank=True,
        verbose_name="Training Syllabus",
        help_text="Training syllabi covered by this manual",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RPAS Operations Manual"
        verbose_name_plural = "RPAS Operations Manuals"
        ordering = ["-version", "-revision_number"]

    def __str__(self):
        return f"{self.manual_id} - {self.title} v{self.version}"

    def save(self, *args, **kwargs):
        """Auto-generate manual ID if not provided"""
        if not self.manual_id:
            # Generate ID based on manual type and current year
            current_year = timezone.now().year
            type_prefix = {
                "operations": "OPS",
                "maintenance": "MNT",
                "training": "TRN",
                "emergency": "EMG",
                "safety": "SMS",
                "quality": "QUA",
            }.get(self.manual_type, "OPS")

            # Find next sequence number for the year
            existing_count = RPASOperationsManual.objects.filter(
                manual_id__startswith=f"{type_prefix}-{current_year}-"
            ).count()

            sequence = str(existing_count + 1).zfill(3)
            self.manual_id = f"{type_prefix}-{current_year}-{sequence}"

        # Set next review date if not provided (default: 1 year)
        if not self.next_review_date and self.effective_date:
            from dateutil.relativedelta import relativedelta

            self.next_review_date = self.effective_date + relativedelta(years=1)

        super().save(*args, **kwargs)

    def clean(self):
        """Validate manual requirements"""
        from django.core.exceptions import ValidationError

        # CASA approval validation
        if self.casa_approved and not self.casa_approval_reference:
            raise ValidationError("CASA approved manuals must have approval reference")

        # Status transition validation
        if self.status == "published" and not self.approved_by:
            raise ValidationError("Published manuals must have organizational approval")

        # Effective date validation
        if self.effective_date and self.effective_date < timezone.now().date():
            if self.status in ["draft", "review"]:
                raise ValidationError(
                    "Draft/review manuals cannot have past effective dates"
                )

    @property
    def is_current(self):
        """Check if manual is current and effective"""
        today = timezone.now().date()
        return (
            self.status == "published"
            and self.effective_date <= today
            and self.next_review_date >= today
        )

    @property
    def days_until_review(self):
        """Calculate days until required review"""
        if self.next_review_date:
            delta = self.next_review_date - timezone.now().date()
            return delta.days
        return None

    @property
    def is_overdue_review(self):
        """Check if manual review is overdue"""
        days_until = self.days_until_review
        return days_until is not None and days_until < 0


class ManualSection(models.Model):
    """
    Major sections within an Operations Manual
    Provides hierarchical document structure
    """

    SECTION_TYPE_CHOICES = [
        ("general", "General"),
        ("operational", "Operational Procedures"),
        ("emergency", "Emergency Procedures"),
        ("safety", "Safety Management"),
        ("training", "Training and Competency"),
        ("maintenance", "Maintenance"),
        ("quality", "Quality Assurance"),
        ("appendix", "Appendix"),
    ]

    operations_manual = models.ForeignKey(
        RPASOperationsManual,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="Operations Manual",
    )

    section_number = models.CharField(
        max_length=10,
        verbose_name="Section Number",
        help_text="Section number (e.g., 1, 2, 3, A, B)",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Section Title",
        help_text="Descriptive title of section",
    )

    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPE_CHOICES,
        verbose_name="Section Type",
        help_text="Category of section content",
    )

    order = models.PositiveIntegerField(
        verbose_name="Display Order", help_text="Order for display in manual"
    )

    content = models.TextField(
        blank=True,
        verbose_name="Section Content",
        help_text="Main content of section (supports HTML/Markdown)",
    )

    # Integration with other systems
    related_sops = models.ManyToManyField(
        StandardOperatingProcedure,
        blank=True,
        verbose_name="Related SOPs",
        help_text="SOPs detailed in this section",
    )

    required_training = models.ManyToManyField(
        TrainingSyllabus,
        blank=True,
        verbose_name="Required Training",
        help_text="Training requirements covered in this section",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Manual Section"
        verbose_name_plural = "Manual Sections"
        ordering = ["operations_manual", "order", "section_number"]
        unique_together = ["operations_manual", "section_number"]

    def __str__(self):
        return f"Section {self.section_number}: {self.title}"


class ManualSubsection(models.Model):
    """
    Subsections within manual sections
    Enables detailed document organization
    """

    section = models.ForeignKey(
        ManualSection,
        on_delete=models.CASCADE,
        related_name="subsections",
        verbose_name="Parent Section",
    )

    subsection_number = models.CharField(
        max_length=10,
        verbose_name="Subsection Number",
        help_text="Subsection number (e.g., 1.1, 1.2, A.1)",
    )

    title = models.CharField(max_length=200, verbose_name="Subsection Title")

    order = models.PositiveIntegerField(verbose_name="Display Order")

    content = models.TextField(
        verbose_name="Subsection Content",
        help_text="Detailed content (supports HTML/Markdown)",
    )

    # CASA Reference Integration
    casa_reference = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="CASA Reference",
        help_text="Specific CASA regulation reference (e.g., 101.073)",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Manual Subsection"
        verbose_name_plural = "Manual Subsections"
        ordering = ["section", "order", "subsection_number"]
        unique_together = ["section", "subsection_number"]

    def __str__(self):
        return f"{self.subsection_number}: {self.title}"


class ManualApprovalHistory(models.Model):
    """
    Document Control - Approval and Change History
    Maintains complete audit trail for CASA compliance
    """

    ACTION_CHOICES = [
        ("created", "Document Created"),
        ("reviewed", "Reviewed"),
        ("approved", "Approved"),
        ("published", "Published"),
        ("revised", "Revised"),
        ("superseded", "Superseded"),
        ("withdrawn", "Withdrawn"),
    ]

    operations_manual = models.ForeignKey(
        RPASOperationsManual,
        on_delete=models.CASCADE,
        related_name="approval_history",
        verbose_name="Operations Manual",
    )

    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, verbose_name="Action"
    )

    action_date = models.DateTimeField(auto_now_add=True, verbose_name="Action Date")

    performed_by = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.PROTECT, verbose_name="Performed By"
    )

    version_at_action = models.CharField(
        max_length=10,
        verbose_name="Version at Action",
        help_text="Document version when action was performed",
    )

    comments = models.TextField(
        blank=True,
        verbose_name="Comments",
        help_text="Comments or notes about the action",
    )

    # Digital Signature Support
    digital_signature = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Digital Signature",
        help_text="Digital signature hash or reference",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Address",
        help_text="IP address of user performing action",
    )

    class Meta:
        verbose_name = "Manual Approval History"
        verbose_name_plural = "Manual Approval Histories"
        ordering = ["-action_date"]

    def __str__(self):
        return (
            f"{self.operations_manual.manual_id} - {self.action} by {self.performed_by}"
        )


class ManualDistributionRecord(models.Model):
    """
    Document Distribution Control
    Tracks who has access to controlled documents
    """

    operations_manual = models.ForeignKey(
        RPASOperationsManual,
        on_delete=models.CASCADE,
        related_name="distribution_records",
        verbose_name="Operations Manual",
    )

    distributed_to = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE, verbose_name="Distributed To"
    )

    distribution_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Distribution Date"
    )

    version_distributed = models.CharField(
        max_length=10, verbose_name="Version Distributed"
    )

    access_granted_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.PROTECT,
        related_name="manual_distributions_granted",
        verbose_name="Access Granted By",
    )

    acknowledgment_required = models.BooleanField(
        default=True,
        verbose_name="Acknowledgment Required",
        help_text="Recipient must acknowledge receipt",
    )

    acknowledged_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Acknowledged Date",
        help_text="Date recipient acknowledged receipt",
    )

    access_revoked = models.BooleanField(default=False, verbose_name="Access Revoked")

    revocation_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Revocation Date"
    )

    class Meta:
        verbose_name = "Manual Distribution Record"
        verbose_name_plural = "Manual Distribution Records"
        ordering = ["-distribution_date"]
        unique_together = ["operations_manual", "distributed_to", "version_distributed"]

    def __str__(self):
        return f"{self.operations_manual.manual_id} v{self.version_distributed} → {self.distributed_to}"

    @property
    def is_current_access(self):
        """Check if user has current access to manual"""
        return not self.access_revoked and self.operations_manual.status == "published"

    @property
    def acknowledgment_overdue(self):
        """Check if acknowledgment is overdue (>7 days)"""
        if self.acknowledgment_required and not self.acknowledged_date:
            from django.utils import timezone

            overdue_date = self.distribution_date + timezone.timedelta(days=7)
            return timezone.now() > overdue_date
        return False
