from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


class RiskRegister(models.Model):
    """
    Risk Register for Mission Risk Assessment
    Based on CASA risk management framework
    """

    LIKELIHOOD_CHOICES = [
        (1, "Extremely Improbable - Almost inconceivable that this event will occur"),
        (2, "Improbable - Very unlikely to occur (not known to have occurred)"),
        (3, "Remote - Unlikely to occur, but possible (has occurred rarely)"),
        (4, "Occasional - Likely to occur sometimes (has occurred infrequently)"),
        (5, "Frequent - Likely to occur many times (has occurred frequently)"),
    ]

    CONSEQUENCE_CHOICES = [
        (
            "E",
            "Negligible - Less than $2,000 impact, Few consequences, managed through normal procedures",
        ),
        (
            "D",
            "Minor - $2,000-$10,000 impact, Minor injury, Operating limitations required, Use of emergency procedures",
        ),
        (
            "C",
            "Moderate - $10,000-$50,000 impact, Serious incident, Injury to persons, Significant reduction in safety margins",
        ),
        (
            "B",
            "Hazardous - $50,000-$100,000 impact, Major incident, Serious injury, Major equipment damage, Major impact to organisation ability",
        ),
        (
            "A",
            "Catastrophic - More than $100,000 impact, Fatality, Equipment destroyed, Threatens the ongoing existence of the organisation",
        ),
    ]

    RISK_LEVEL_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    ACCEPTANCE_LEVEL_CHOICES = [
        ("ceo", "CEO"),
        ("chief_remote_pilot", "Chief Remote Pilot"),
    ]

    # Risk Identification
    reference_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Reference Number",
        help_text="Unique risk reference number",
    )

    mission = models.ForeignKey(
        "Mission",
        on_delete=models.CASCADE,
        related_name="risk_registers",
        verbose_name="Mission",
        help_text="Associated mission",
    )

    date_entered = models.DateField(
        default=timezone.now,
        verbose_name="Date Entered in Register",
        help_text="Date risk was entered in register",
    )

    hazard = models.TextField(
        verbose_name="Hazard", help_text="Description of the hazard"
    )

    risk_description = models.TextField(
        verbose_name="Risk Description", help_text="Detailed description of the risk"
    )

    # Existing Controls
    existing_controls = models.TextField(
        verbose_name="Existing Controls",
        help_text="Current controls in place to manage risk",
    )

    # Initial Risk Assessment
    initial_likelihood = models.PositiveSmallIntegerField(
        choices=LIKELIHOOD_CHOICES,
        verbose_name="Initial Likelihood",
        help_text="Initial likelihood rating (1-5)",
    )

    initial_consequence = models.CharField(
        max_length=1,
        choices=CONSEQUENCE_CHOICES,
        verbose_name="Initial Consequence",
        help_text="Initial consequence rating (A-E)",
    )

    initial_risk_rating = models.CharField(
        max_length=3,
        blank=True,
        verbose_name="Initial Risk Rating",
        help_text="Calculated initial risk rating (e.g., 3C)",
    )

    # Additional Controls
    additional_controls = models.TextField(
        blank=True,
        verbose_name="Additional Controls",
        help_text="Additional controls to be implemented",
    )

    # Residual Risk Assessment
    residual_likelihood = models.PositiveSmallIntegerField(
        choices=LIKELIHOOD_CHOICES,
        verbose_name="Residual Likelihood",
        help_text="Residual likelihood rating after additional controls",
    )

    residual_consequence = models.CharField(
        max_length=1,
        choices=CONSEQUENCE_CHOICES,
        verbose_name="Residual Consequence",
        help_text="Residual consequence rating after additional controls",
    )

    residual_risk_rating = models.CharField(
        max_length=3,
        blank=True,
        verbose_name="Residual Risk Rating",
        help_text="Calculated residual risk rating",
    )

    # Risk Management
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        blank=True,
        verbose_name="Risk Level",
        help_text="Overall risk level classification",
    )

    acceptance_level = models.CharField(
        max_length=20,
        choices=ACCEPTANCE_LEVEL_CHOICES,
        blank=True,
        verbose_name="Acceptance Level",
        help_text="Required approval level for this risk",
    )

    risk_owner = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        verbose_name="Risk Owner",
        help_text="Person responsible for managing this risk",
    )

    review_due_date = models.DateField(
        verbose_name="Review Due Date", help_text="Date when risk should be reviewed"
    )

    # Actions Required
    actions_required = models.TextField(
        blank=True,
        verbose_name="Actions Required",
        help_text="Specific actions required based on risk level",
    )

    # Status
    risk_accepted = models.BooleanField(
        default=False,
        verbose_name="Risk Accepted",
        help_text="Risk has been formally accepted",
    )

    accepted_by = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="accepted_risks",
        null=True,
        blank=True,
        verbose_name="Accepted By",
        help_text="Person who accepted the risk",
    )

    accepted_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Accepted Date",
        help_text="Date/time when risk was accepted",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Risk Register"
        verbose_name_plural = "Risk Registers"
        ordering = ["-date_entered"]

    def __str__(self):
        return f"{self.reference_number} - {self.hazard[:50]}"

    def save(self, *args, **kwargs):
        """Auto-calculate risk ratings and levels"""
        # Calculate initial risk rating
        self.initial_risk_rating = (
            f"{self.initial_likelihood}{self.initial_consequence}"
        )

        # Calculate residual risk rating
        self.residual_risk_rating = (
            f"{self.residual_likelihood}{self.residual_consequence}"
        )

        # Determine risk level based on residual risk matrix
        self.risk_level = self._calculate_risk_level(
            self.residual_likelihood, self.residual_consequence
        )

        # Set acceptance level based on risk level
        if self.risk_level == "high":
            self.acceptance_level = "ceo"
            self.actions_required = "Activity must be suspended. Risk considered unacceptable and requires new concept of operation."
        elif self.risk_level == "medium":
            self.acceptance_level = "chief_remote_pilot"
            self.actions_required = "Risk should be mitigated to ALARP. Activity can continue only after acceptance from chief remote pilot or senior manager."
        else:
            self.acceptance_level = "chief_remote_pilot"
            self.actions_required = "Risk is acceptable and activity may continue providing due consideration has been given to the activity."

        super().save(*args, **kwargs)

    def _calculate_risk_level(self, likelihood, consequence):
        """Calculate risk level based on risk matrix"""
        # Risk matrix based on your attachment
        risk_matrix = {
            # Likelihood 5 (Frequent)
            (5, "A"): "high",
            (5, "B"): "high",
            (5, "C"): "high",
            (5, "D"): "medium",
            (5, "E"): "low",
            # Likelihood 4 (Occasional)
            (4, "A"): "high",
            (4, "B"): "high",
            (4, "C"): "medium",
            (4, "D"): "medium",
            (4, "E"): "low",
            # Likelihood 3 (Remote)
            (3, "A"): "high",
            (3, "B"): "medium",
            (3, "C"): "medium",
            (3, "D"): "low",
            (3, "E"): "low",
            # Likelihood 2 (Improbable)
            (2, "A"): "medium",
            (2, "B"): "medium",
            (2, "C"): "low",
            (2, "D"): "low",
            (2, "E"): "low",
            # Likelihood 1 (Extremely Improbable)
            (1, "A"): "medium",
            (1, "B"): "low",
            (1, "C"): "low",
            (1, "D"): "low",
            (1, "E"): "low",
        }

        return risk_matrix.get((likelihood, consequence), "medium")

    @property
    def requires_ceo_approval(self):
        """Check if risk requires CEO approval"""
        return self.risk_level == "high"

    def clean(self):
        """Validate risk register data"""
        if self.risk_accepted and not self.accepted_by:
            raise ValidationError(
                "Risk cannot be accepted without specifying who accepted it"
            )

        if self.review_due_date < timezone.now().date():
            raise ValidationError("Review due date cannot be in the past")


class JobSafetyAssessment(models.Model):
    """
    Job Safety Assessment (JSA) for Mission Operations
    Section 1: Risk Assessment and Section 2: Job Safety Assessment
    """

    OPERATION_TYPE_CHOICES = [
        (
            "soc",
            "Standard Operating Conditions (SOC) - RPA not heavier than 2kg, no official authorisation required",
        ),
        ("reoc", "Remote Operator Certificate (ReOC) operations"),
        ("casa_approval", "Operations requiring specific CASA approval"),
    ]

    AIRSPACE_CLASS_CHOICES = [
        ("G", "Class G - Uncontrolled Airspace"),
        ("E", "Class E - Controlled Airspace"),
        ("D", "Class D - Controlled Airspace"),
        ("C", "Class C - Controlled Airspace"),
        ("PRD", "Prohibited, Restricted, or Danger Area"),
    ]

    FLIGHT_TYPE_CHOICES = [
        ("VLOS", "Visual Line of Sight"),
        ("EVLOS", "Extended Visual Line of Sight"),
        ("BVLOS", "Beyond Visual Line of Sight"),
        ("DAY", "Day Operations"),
        ("NIGHT", "Night Operations"),
    ]

    # JSA Identification
    jsa_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="JSA ID",
        help_text="Unique Job Safety Assessment identifier",
        validators=[
            RegexValidator(
                regex=r"^JSA-\d{4}-\d{6}$", message="Format: JSA-YYYY-XXXXXX"
            )
        ],
    )

    mission = models.OneToOneField(
        "Mission",
        on_delete=models.CASCADE,
        verbose_name="Mission",
        help_text="Associated mission",
    )

    # Section 1: Risk Assessment
    operation_type = models.CharField(
        max_length=20,
        choices=OPERATION_TYPE_CHOICES,
        verbose_name="Operation Type",
        help_text="Type of RPA operation under CASA regulations",
    )

    # Operating Area Map
    operating_area_map = models.TextField(
        verbose_name="Map of Operating Area",
        help_text="Description of operating area showing launch and landing locations and any relevant hazards",
    )

    # Airspace Information
    airspace_class = models.CharField(
        max_length=10,
        choices=AIRSPACE_CLASS_CHOICES,
        verbose_name="Airspace Class(es) and Height(s)",
        help_text="Airspace classification for operating area",
    )

    maximum_operating_height_agl = models.PositiveIntegerField(
        verbose_name="Maximum Operating Height (ft AGL)",
        help_text="Maximum operating height above ground level",
        validators=[MaxValueValidator(400)],
    )

    maximum_operating_altitude_amsl = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maximum Operating Altitude (ft AMSL)",
        help_text="Maximum operating altitude above mean sea level",
    )

    # Nearby Facilities
    nearby_aerodromes = models.TextField(
        blank=True,
        verbose_name="Nearby Aerodromes",
        help_text="Include location, distance, type of nearby aerodromes",
    )

    aeronautical_radio_frequencies = models.TextField(
        blank=True,
        verbose_name="Aeronautical Radio Frequencies",
        help_text="Relevant radio frequencies for area coordination",
    )

    # Flight Types
    flight_types = models.JSONField(
        default=list,
        verbose_name="Flight Types",
        help_text="Types of flights to be conducted (VLOS, EVLOS, BVLOS, DAY, NIGHT)",
    )

    # Hazards and Mitigations
    airspace_hazards = models.TextField(
        blank=True,
        verbose_name="Airspace Hazards and Mitigations",
        help_text="Airspace-related hazards and mitigation strategies",
    )

    ground_hazards = models.TextField(
        blank=True,
        verbose_name="Ground Hazards and Mitigations",
        help_text="Ground hazards and mitigations (people, obstacles, interference, etc.)",
    )

    # SOP Adequacy Assessment
    sop_adequate = models.BooleanField(
        default=False,
        verbose_name="Does SOP adequately mitigate all hazards?",
        help_text="Standard Operating Procedures adequately address all identified hazards",
    )

    unmitigated_hazards = models.TextField(
        blank=True,
        verbose_name="Unmitigated Hazards Details",
        help_text="Detail unmitigated hazards if SOP is not adequate",
    )

    # Preliminary Assessment
    preliminary_assessment_accurate = models.BooleanField(
        default=False,
        verbose_name="Preliminary Assessment/JSA Accurate",
        help_text="Preliminary assessment or JSA is accurate and complete",
    )

    assessment_changes = models.TextField(
        blank=True,
        verbose_name="Assessment Changes",
        help_text="Record changes here if preliminary assessment needs updates",
    )

    # Operating Restrictions
    additional_operating_restrictions = models.TextField(
        blank=True,
        verbose_name="Additional Operating Restrictions/Limitations",
        help_text="Additional restrictions or limitations for this operation",
    )

    # Official Authorization
    official_authorization = models.TextField(
        blank=True,
        verbose_name="Official Authorisation Obtained",
        help_text="Identification of official authorisation obtained (if applicable)",
    )

    # Flight Authorization
    flight_authorized = models.BooleanField(
        default=False,
        verbose_name="Flight Authorised?",
        help_text="Flight has been authorized to proceed",
    )

    authorized_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date(s) Approved for Operations",
        help_text="Date when operations were approved",
    )

    approved_aircraft_types = models.TextField(
        blank=True,
        verbose_name="RPA Types/Models Approved for Operations",
        help_text="Specific aircraft types approved for these operations",
    )

    # Approvals
    crp_approval_signature = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="CRP/ARN Signature",
        help_text="Chief Remote Pilot or ARN signature",
    )

    crp_approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="CRP/ARN Approval Date",
        help_text="Date of CRP or ARN approval",
    )

    rp_approval_signature = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="RP/ARN Signature",
        help_text="Remote Pilot or ARN signature",
    )

    rp_approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="RP/ARN Approval Date",
        help_text="Date of RP or ARN approval",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Safety Assessment"
        verbose_name_plural = "Job Safety Assessments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.jsa_id} - {self.mission.name}"

    @property
    def is_fully_approved(self):
        """Check if JSA has all required approvals"""
        if not self.flight_authorized:
            return False

        # Check that both sections are signed
        if not (self.section1_approval_signature and self.section1_approval_date):
            return False

        if not (self.section2_approval_signature and self.section2_approval_date):
            return False

        # Check that assessment is accurate
        if not self.preliminary_assessment_accurate:
            return False

        return True

    def save(self, *args, **kwargs):
        """Auto-generate JSA ID if not provided"""
        if not self.jsa_id:
            year = timezone.now().year
            last_jsa = (
                JobSafetyAssessment.objects.filter(jsa_id__startswith=f"JSA-{year}-")
                .order_by("jsa_id")
                .last()
            )

            if last_jsa:
                last_seq = int(last_jsa.jsa_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.jsa_id = f"JSA-{year}-{next_seq:06d}"

        super().save(*args, **kwargs)

    def clean(self):
        """Validate JSA requirements"""
        # Flight authorization validation
        if self.flight_authorized:
            if not self.crp_approval_signature or not self.crp_approval_date:
                raise ValidationError(
                    "Flight authorization requires CRP signature and date"
                )

            if self.operation_type != "soc" and (
                not self.rp_approval_signature or not self.rp_approval_date
            ):
                raise ValidationError(
                    "Non-SOC operations require both CRP and RP approval"
                )

        # SOP adequacy validation
        if not self.sop_adequate and not self.unmitigated_hazards:
            raise ValidationError(
                "If SOP is not adequate, unmitigated hazards must be detailed"
            )

    @property
    def is_soc_operation(self):
        """Check if this is a Standard Operating Conditions operation"""
        return self.operation_type == "soc"

    @property
    def requires_casa_approval(self):
        """Check if operation requires specific CASA approval"""
        return self.operation_type == "casa_approval"

    @property
    def is_fully_approved(self):
        """Check if JSA is fully approved and ready for operations"""
        if not self.flight_authorized:
            return False

        if not self.crp_approval_signature or not self.crp_approval_date:
            return False

        # Non-SOC operations need additional approvals
        if self.operation_type != "soc":
            if not self.rp_approval_signature or not self.rp_approval_date:
                return False

        return True


class Mission(models.Model):
    """
    Mission definition for RPA operations
    CASA Part 101 compliant mission planning and authorization
    """

    MISSION_TYPE_CHOICES = [
        ("commercial", "Commercial Operations"),
        ("training", "Training Operations"),
        ("research", "Research & Development"),
        ("emergency", "Emergency Services"),
        ("surveillance", "Surveillance"),
        ("mapping", "Aerial Mapping"),
        ("inspection", "Infrastructure Inspection"),
        ("delivery", "Delivery Operations"),
        ("photography", "Aerial Photography"),
        ("agricultural", "Agricultural Operations"),
        ("recreational", "Recreational"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("approved", "Approved"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("suspended", "Suspended"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low Priority"),
        ("medium", "Medium Priority"),
        ("high", "High Priority"),
        ("critical", "Critical"),
    ]

    # Mission Identification
    mission_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Mission ID",
        help_text="Unique mission identifier",
        validators=[
            RegexValidator(
                regex=r"^MSN-\d{4}-\d{6}$", message="Format: MSN-YYYY-XXXXXX"
            )
        ],
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Mission Name",
        help_text="Descriptive mission name",
    )

    mission_type = models.CharField(
        max_length=20,
        choices=MISSION_TYPE_CHOICES,
        verbose_name="Mission Type",
        help_text="Type of RPA operation",
    )

    # Mission Details
    description = models.TextField(
        verbose_name="Mission Description",
        help_text="Detailed description of mission objectives",
    )

    client = models.ForeignKey(
        "accounts.ClientProfile",
        on_delete=models.PROTECT,
        verbose_name="Client",
        help_text="Client requesting the mission",
    )

    mission_commander = models.ForeignKey(
        "accounts.StaffProfile",
        on_delete=models.PROTECT,
        related_name="commanded_missions",
        verbose_name="Mission Commander",
        help_text="Person responsible for mission oversight",
    )

    # Status and Priority
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planning",
        verbose_name="Mission Status",
        help_text="Current mission status",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="Priority Level",
        help_text="Mission priority level",
    )

    # Scheduling
    planned_start_date = models.DateTimeField(
        verbose_name="Planned Start Date", help_text="Planned mission start date/time"
    )

    planned_end_date = models.DateTimeField(
        verbose_name="Planned End Date", help_text="Planned mission end date/time"
    )

    actual_start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Actual Start Date",
        help_text="Actual mission start date/time",
    )

    actual_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Actual End Date",
        help_text="Actual mission end date/time",
    )

    # CASA Compliance
    casa_authorization_required = models.BooleanField(
        default=False,
        verbose_name="CASA Authorization Required",
        help_text="Mission requires specific CASA authorization",
    )

    casa_authorization_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="CASA Authorization Reference",
        help_text="CASA authorization or exemption reference",
    )

    # Risk Assessment & JSA Requirements
    risk_assessment_required = models.BooleanField(
        default=True,
        verbose_name="Risk Assessment Required",
        help_text="Mission requires formal risk assessment",
    )

    jsa_required = models.BooleanField(
        default=True,
        verbose_name="JSA Required",
        help_text="Mission requires Job Safety Assessment",
    )

    overall_risk_level = models.CharField(
        max_length=10,
        choices=[
            ("low", "Low Risk"),
            ("medium", "Medium Risk"),
            ("high", "High Risk"),
        ],
        blank=True,
        verbose_name="Overall Risk Level",
        help_text="Overall assessed risk level from risk register",
    )

    # Risk Management Approval
    risk_accepted_by_ceo = models.BooleanField(
        default=False,
        verbose_name="Risk Accepted by CEO",
        help_text="High risk operations have been accepted by CEO",
    )

    risk_accepted_by_crp = models.BooleanField(
        default=False,
        verbose_name="Risk Accepted by Chief Remote Pilot",
        help_text="Medium/Low risk operations accepted by Chief Remote Pilot",
    )

    # Documentation
    briefing_notes = models.TextField(
        blank=True,
        verbose_name="Briefing Notes",
        help_text="Mission briefing notes and considerations",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mission"
        verbose_name_plural = "Missions"
        ordering = ["-planned_start_date"]

    def __str__(self):
        return f"{self.mission_id} - {self.name}"

    def clean(self):
        """Validate mission parameters and compliance requirements"""
        # Basic date validation
        if self.planned_end_date <= self.planned_start_date:
            raise ValidationError("End date must be after start date")

        if (
            self.actual_start_date
            and self.actual_end_date
            and self.actual_end_date <= self.actual_start_date
        ):
            raise ValidationError("Actual end date must be after actual start date")

        # Risk Assessment and JSA validation for approved/active missions
        if self.status in ["approved", "active"]:
            if self.risk_assessment_required and not self.has_completed_risk_assessment:
                raise ValidationError(
                    "Mission cannot be approved without completed risk assessment"
                )

            if self.jsa_required and not self.has_completed_jsa:
                raise ValidationError(
                    "Mission cannot be approved without completed Job Safety Assessment"
                )

            # Check risk acceptance requirements
            if self.overall_risk_level == "high" and not self.risk_accepted_by_ceo:
                raise ValidationError(
                    "High risk missions must be accepted by CEO before approval"
                )

            if (
                self.overall_risk_level in ["medium", "low"]
                and not self.risk_accepted_by_crp
            ):
                raise ValidationError(
                    "Medium/Low risk missions must be accepted by Chief Remote Pilot before approval"
                )

    @property
    def is_active(self):
        """Check if mission is currently active"""
        return self.status == "active"

    @property
    def duration_planned(self):
        """Calculate planned mission duration"""
        return self.planned_end_date - self.planned_start_date

    @property
    def duration_actual(self):
        """Calculate actual mission duration"""
        if self.actual_start_date and self.actual_end_date:
            return self.actual_end_date - self.actual_start_date
        return None

    @property
    def has_completed_risk_assessment(self):
        """Check if mission has completed risk assessment"""
        if not self.risk_assessment_required:
            return True

        # Must have at least one risk register entry with accepted risks
        risk_registers = self.risk_registers.all()
        if not risk_registers.exists():
            return False

        # All high-level risks must be accepted
        high_risks = risk_registers.filter(risk_level="high")
        if (
            high_risks.exists()
            and not high_risks.filter(risk_accepted=True).count() == high_risks.count()
        ):
            return False

        # Calculate overall risk level from all risk registers
        risk_levels = list(risk_registers.values_list("risk_level", flat=True))
        if "high" in risk_levels:
            self.overall_risk_level = "high"
        elif "medium" in risk_levels:
            self.overall_risk_level = "medium"
        else:
            self.overall_risk_level = "low"

        return True

    @property
    def has_completed_jsa(self):
        """Check if mission has completed Job Safety Assessment"""
        if not self.jsa_required:
            return True

        try:
            jsa = self.jobsafetyassessment
            return jsa.is_fully_approved
        except JobSafetyAssessment.DoesNotExist:
            return False

    @property
    def is_ready_for_approval(self):
        """Check if mission is ready for approval"""
        if self.status != "planning":
            return False

        if self.risk_assessment_required and not self.has_completed_risk_assessment:
            return False

        if self.jsa_required and not self.has_completed_jsa:
            return False

        # Check risk acceptance
        if self.overall_risk_level == "high" and not self.risk_accepted_by_ceo:
            return False

        if (
            self.overall_risk_level in ["medium", "low"]
            and not self.risk_accepted_by_crp
        ):
            return False

        return True

    @property
    def risk_assessment_summary(self):
        """Get summary of risk assessment status"""
        if not self.risk_assessment_required:
            return "Not Required"

        risk_registers = self.risk_registers.all()
        if not risk_registers.exists():
            return "Pending - No Risk Registers"

        total_risks = risk_registers.count()
        accepted_risks = risk_registers.filter(risk_accepted=True).count()

        if accepted_risks == total_risks:
            return f"Complete - {total_risks} risks assessed and accepted"
        else:
            return f"Incomplete - {accepted_risks}/{total_risks} risks accepted"

    @property
    def jsa_status(self):
        """Get JSA completion status"""
        if not self.jsa_required:
            return "Not Required"

        try:
            jsa = self.jobsafetyassessment
            if jsa.is_fully_approved:
                return "Complete - JSA Approved"
            else:
                return "Incomplete - Awaiting Approvals"
        except JobSafetyAssessment.DoesNotExist:
            return "Pending - JSA Not Created"

    def save(self, *args, **kwargs):
        """Auto-generate mission ID if not provided"""
        if not self.mission_id:
            year = timezone.now().year
            last_mission = (
                Mission.objects.filter(mission_id__startswith=f"MSN-{year}-")
                .order_by("mission_id")
                .last()
            )

            if last_mission:
                last_seq = int(last_mission.mission_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.mission_id = f"MSN-{year}-{next_seq:06d}"

        super().save(*args, **kwargs)


class FlightPlan(models.Model):
    """
    Individual Flight Plan for RPA Operations
    CASA Part 101 compliant flight planning
    """

    FLIGHT_TYPE_CHOICES = [
        ("line_of_sight", "Visual Line of Sight (VLOS)"),
        ("extended_vlos", "Extended Visual Line of Sight (EVLOS)"),
        ("beyond_vlos", "Beyond Visual Line of Sight (BVLOS)"),
        ("night_operations", "Night Operations"),
        ("controlled_airspace", "Controlled Airspace Operations"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted for Approval"),
        ("approved", "Approved"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    # Flight Plan Identification
    flight_plan_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Flight Plan ID",
        help_text="Unique flight plan identifier",
        validators=[
            RegexValidator(
                regex=r"^FPL-\d{4}-\d{6}$", message="Format: FPL-YYYY-XXXXXX"
            )
        ],
    )

    # Related Objects
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        verbose_name="Mission",
        help_text="Associated mission",
    )

    aircraft = models.ForeignKey(
        "aircraft.Aircraft",
        on_delete=models.PROTECT,
        verbose_name="Aircraft",
        help_text="Aircraft for this flight",
    )

    pilot_in_command = models.ForeignKey(
        "accounts.PilotProfile",
        on_delete=models.PROTECT,
        related_name="commanded_flights",
        verbose_name="Pilot in Command",
        help_text="Remote pilot in command",
    )

    remote_pilot_observer = models.ForeignKey(
        "accounts.PilotProfile",
        on_delete=models.PROTECT,
        related_name="observed_flights",
        null=True,
        blank=True,
        verbose_name="Remote Pilot Observer",
        help_text="Observer pilot (if required)",
    )

    # Flight Details
    flight_type = models.CharField(
        max_length=20,
        choices=FLIGHT_TYPE_CHOICES,
        verbose_name="Flight Type",
        help_text="Type of flight operation",
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Status",
        help_text="Current flight plan status",
    )

    # Operational Area
    operational_area = models.ForeignKey(
        "airspace.OperationalArea",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Operational Area",
        help_text="Defined operational area (if applicable)",
    )

    departure_location = models.CharField(
        max_length=200,
        verbose_name="Departure Location",
        help_text="Departure location description",
    )

    departure_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Departure Latitude",
        help_text="Departure latitude in decimal degrees",
    )

    departure_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Departure Longitude",
        help_text="Departure longitude in decimal degrees",
    )

    # Flight Parameters
    planned_altitude_agl = models.PositiveIntegerField(
        verbose_name="Planned Altitude AGL (feet)",
        help_text="Planned operating altitude above ground level",
        validators=[MaxValueValidator(400)],  # Part 101 standard limit
    )

    maximum_range_from_pilot = models.PositiveIntegerField(
        verbose_name="Maximum Range from Pilot (meters)",
        help_text="Maximum distance from remote pilot",
        validators=[MaxValueValidator(500)],  # VLOS limit
    )

    # Timing
    planned_departure_time = models.DateTimeField(
        verbose_name="Planned Departure Time", help_text="Planned flight departure time"
    )

    estimated_flight_time = models.DurationField(
        verbose_name="Estimated Flight Time", help_text="Estimated duration of flight"
    )

    actual_departure_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Actual Departure Time",
        help_text="Actual flight departure time",
    )

    actual_landing_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Actual Landing Time",
        help_text="Actual flight landing time",
    )

    # Weather and Conditions
    weather_minimums = models.TextField(
        verbose_name="Weather Minimums",
        help_text="Minimum weather conditions for flight",
    )

    planned_weather_check_time = models.DateTimeField(
        verbose_name="Planned Weather Check Time",
        help_text="When weather will be checked before flight",
    )

    # CASA Compliance
    notam_checked = models.BooleanField(
        default=False,
        verbose_name="NOTAM Checked",
        help_text="NOTAMs have been checked",
    )

    airspace_coordination_required = models.BooleanField(
        default=False,
        verbose_name="Airspace Coordination Required",
        help_text="Requires coordination with ATC or other authorities",
    )

    airspace_coordination_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Airspace Coordination Reference",
        help_text="ATC clearance or coordination reference",
    )

    # Safety
    emergency_procedures = models.TextField(
        verbose_name="Emergency Procedures",
        help_text="Emergency procedures for this flight",
    )

    lost_link_procedures = models.TextField(
        verbose_name="Lost Link Procedures",
        help_text="Procedures if communication link is lost",
    )

    # Route Planning (JSON format for waypoints)
    route_waypoints = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Route Waypoints",
        help_text="Flight route waypoints in JSON format",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Flight Plan"
        verbose_name_plural = "Flight Plans"
        ordering = ["-planned_departure_time"]

    def __str__(self):
        return f"{self.flight_plan_id} - {self.aircraft.registration_mark}"

    def clean(self):
        """Validate flight plan parameters"""
        # Validate coordinates
        if not (-90 <= self.departure_latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90 degrees")

        if not (-180 <= self.departure_longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180 degrees")

        # Validate altitude for flight type
        if self.flight_type == "line_of_sight" and self.planned_altitude_agl > 120:
            raise ValidationError("VLOS operations typically limited to 120ft AGL")

        # Validate range for VLOS
        if self.flight_type == "line_of_sight" and self.maximum_range_from_pilot > 500:
            raise ValidationError("VLOS operations limited to 500m from pilot")

    @property
    def is_completed(self):
        """Check if flight is completed"""
        return self.status == "completed"

    @property
    def actual_flight_duration(self):
        """Calculate actual flight duration"""
        if self.actual_departure_time and self.actual_landing_time:
            return self.actual_landing_time - self.actual_departure_time
        return None

    def save(self, *args, **kwargs):
        """Auto-generate flight plan ID if not provided"""
        if not self.flight_plan_id:
            year = timezone.now().year
            last_plan = (
                FlightPlan.objects.filter(flight_plan_id__startswith=f"FPL-{year}-")
                .order_by("flight_plan_id")
                .last()
            )

            if last_plan:
                last_seq = int(last_plan.flight_plan_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.flight_plan_id = f"FPL-{year}-{next_seq:06d}"

        super().save(*args, **kwargs)


class FlightLog(models.Model):
    """
    Flight Log Entry for completed flights
    CASA Part 101 compliant flight record keeping
    """

    LOG_ENTRY_CHOICES = [
        ("normal", "Normal Flight"),
        ("training", "Training Flight"),
        ("test", "Test Flight"),
        ("maintenance_test", "Maintenance Test Flight"),
        ("emergency_return", "Emergency Return"),
        ("incident", "Incident Flight"),
    ]

    # Log Identification
    log_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Log ID",
        help_text="Unique flight log identifier",
        validators=[
            RegexValidator(
                regex=r"^LOG-\d{4}-\d{6}$", message="Format: LOG-YYYY-XXXXXX"
            )
        ],
    )

    # Related Objects
    flight_plan = models.OneToOneField(
        FlightPlan,
        on_delete=models.CASCADE,
        verbose_name="Flight Plan",
        help_text="Associated flight plan",
    )

    # Flight Performance
    takeoff_time = models.DateTimeField(
        verbose_name="Takeoff Time", help_text="Actual takeoff time"
    )

    landing_time = models.DateTimeField(
        verbose_name="Landing Time", help_text="Actual landing time"
    )

    flight_time = models.DurationField(
        verbose_name="Flight Time", help_text="Total flight time"
    )

    maximum_altitude_achieved = models.PositiveIntegerField(
        verbose_name="Maximum Altitude Achieved (feet AGL)",
        help_text="Highest altitude reached during flight",
    )

    maximum_range_achieved = models.PositiveIntegerField(
        verbose_name="Maximum Range Achieved (meters)",
        help_text="Furthest distance from takeoff point",
    )

    # Aircraft Performance
    pre_flight_battery_voltage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Pre-flight Battery Voltage",
        help_text="Battery voltage before flight",
    )

    post_flight_battery_voltage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Post-flight Battery Voltage",
        help_text="Battery voltage after flight",
    )

    # Weather Conditions
    wind_speed_takeoff = models.PositiveIntegerField(
        verbose_name="Wind Speed at Takeoff (knots)",
        help_text="Wind speed at takeoff",
    )

    wind_direction_takeoff = models.PositiveIntegerField(
        verbose_name="Wind Direction at Takeoff (degrees)",
        help_text="Wind direction at takeoff",
        validators=[MaxValueValidator(360)],
    )

    temperature_celsius = models.IntegerField(
        verbose_name="Temperature (°C)", help_text="Temperature during flight"
    )

    visibility_meters = models.PositiveIntegerField(
        verbose_name="Visibility (meters)", help_text="Visibility during flight"
    )

    # Flight Details
    log_entry_type = models.CharField(
        max_length=20,
        choices=LOG_ENTRY_CHOICES,
        default="normal",
        verbose_name="Log Entry Type",
        help_text="Type of flight log entry",
    )

    objectives_achieved = models.BooleanField(
        default=True,
        verbose_name="Objectives Achieved",
        help_text="Flight objectives were achieved",
    )

    # Issues and Observations
    technical_issues = models.TextField(
        blank=True,
        verbose_name="Technical Issues",
        help_text="Any technical issues encountered",
    )

    weather_issues = models.TextField(
        blank=True,
        verbose_name="Weather Issues",
        help_text="Any weather-related issues",
    )

    operational_notes = models.TextField(
        blank=True,
        verbose_name="Operational Notes",
        help_text="General operational notes and observations",
    )

    lessons_learned = models.TextField(
        blank=True,
        verbose_name="Lessons Learned",
        help_text="Lessons learned from this flight",
    )

    # Pilot Assessment
    pilot_performance_notes = models.TextField(
        blank=True,
        verbose_name="Pilot Performance Notes",
        help_text="Notes on pilot performance (for training flights)",
    )

    # CASA Compliance
    regulatory_compliance_notes = models.TextField(
        blank=True,
        verbose_name="Regulatory Compliance Notes",
        help_text="Notes on regulatory compliance during flight",
    )

    # Data Collection
    data_collected = models.TextField(
        blank=True,
        verbose_name="Data Collected",
        help_text="Description of data/imagery collected",
    )

    file_references = models.TextField(
        blank=True,
        verbose_name="File References",
        help_text="References to collected files, images, or data",
    )

    # Maintenance
    maintenance_required = models.BooleanField(
        default=False,
        verbose_name="Maintenance Required",
        help_text="Aircraft requires maintenance after this flight",
    )

    maintenance_notes = models.TextField(
        blank=True,
        verbose_name="Maintenance Notes",
        help_text="Notes for maintenance personnel",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Flight Log"
        verbose_name_plural = "Flight Logs"
        ordering = ["-takeoff_time"]

    def __str__(self):
        return f"{self.log_id} - {self.flight_plan.aircraft.registration_mark} ({self.takeoff_time.strftime('%d/%m/%Y')})"

    def clean(self):
        """Validate flight log parameters"""
        if self.landing_time <= self.takeoff_time:
            raise ValidationError("Landing time must be after takeoff time")

        # Calculate and validate flight time
        calculated_time = self.landing_time - self.takeoff_time
        if abs((calculated_time - self.flight_time).total_seconds()) > 60:
            raise ValidationError("Flight time doesn't match takeoff/landing times")

    @property
    def total_flight_hours(self):
        """Get flight time in decimal hours"""
        return self.flight_time.total_seconds() / 3600

    @property
    def average_ground_speed(self):
        """Calculate average ground speed if range data available"""
        if self.maximum_range_achieved and self.flight_time:
            # Simple calculation - could be enhanced with route data
            distance_km = self.maximum_range_achieved / 1000
            time_hours = self.flight_time.total_seconds() / 3600
            return distance_km / time_hours if time_hours > 0 else 0
        return None

    def save(self, *args, **kwargs):
        """Auto-generate log ID if not provided"""
        if not self.log_id:
            year = timezone.now().year
            last_log = (
                FlightLog.objects.filter(log_id__startswith=f"LOG-{year}-")
                .order_by("log_id")
                .last()
            )

            if last_log:
                last_seq = int(last_log.log_id[-6:])
                next_seq = last_seq + 1
            else:
                next_seq = 1

            self.log_id = f"LOG-{year}-{next_seq:06d}"

        super().save(*args, **kwargs)
