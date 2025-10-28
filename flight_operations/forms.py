from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    AircraftFlightPlan,
    DroneFlightPlan,
    FlightLog,
    JobSafetyAssessment,
    Mission,
    MissionAssignment,
    RiskRegister,
)


class MissionForm(forms.ModelForm):
    """Form for creating and editing missions"""

    class Meta:
        model = Mission
        fields = [
            "mission_id",
            "name",
            "mission_type",
            "description",
            "client",
            "mission_commander",
            "status",
            "priority",
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
            "casa_authorization_required",
            "casa_authorization_reference",
            "risk_assessment_required",
            "jsa_required",
            "overall_risk_level",
            "risk_accepted_by_ceo",
            "risk_accepted_by_crp",
            "briefing_notes",
            # Assignment and Crew fields
            "assigned_pilot",
            "crew_members",
            # Additional Mission Details
            "estimated_duration",
            "weather_requirements",
            "special_requirements",
            "notes",
        ]

        widgets = {
            "mission_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "MSN-YYYY-XXXXXX (leave blank for auto-generation)",
                    "pattern": "^MSN-\\d{4}-\\d{6}$",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter descriptive mission name",
                }
            ),
            "mission_type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Detailed description of mission objectives and requirements",
                }
            ),
            "client": forms.Select(attrs={"class": "form-select"}),
            "mission_commander": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "planned_start_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "planned_end_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "actual_start_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "actual_end_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "casa_authorization_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "casa_authorization_reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CASA authorization or exemption reference number",
                }
            ),
            "risk_assessment_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "jsa_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "overall_risk_level": forms.Select(attrs={"class": "form-select"}),
            "risk_accepted_by_ceo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "risk_accepted_by_crp": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "briefing_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Mission briefing notes and special considerations",
                }
            ),
            # Assignment and Crew widgets
            "assigned_pilot": forms.Select(attrs={"class": "form-select"}),
            "crew_members": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                    "multiple": True,
                    "size": "4",
                }
            ),
            # Additional Mission Details widgets
            "estimated_duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.25",
                    "min": "0",
                    "placeholder": "Hours (e.g., 2.5)",
                }
            ),
            "weather_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Specific weather conditions required for this mission",
                }
            ),
            "special_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Special equipment, permissions, or considerations required",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional notes and operational considerations",
                }
            ),
        }

        labels = {
            "mission_id": "Mission ID",
            "name": "Mission Name",
            "mission_type": "Mission Type",
            "description": "Mission Description",
            "client": "Client",
            "mission_commander": "Mission Commander",
            "status": "Mission Status",
            "priority": "Priority Level",
            "planned_start_date": "Planned Start Date/Time",
            "planned_end_date": "Planned End Date/Time",
            "actual_start_date": "Actual Start Date/Time",
            "actual_end_date": "Actual End Date/Time",
            "casa_authorization_required": "CASA Authorization Required",
            "casa_authorization_reference": "CASA Authorization Reference",
            "risk_assessment_required": "Risk Assessment Required",
            "jsa_required": "Job Safety Assessment Required",
            "overall_risk_level": "Overall Risk Level",
            "risk_accepted_by_ceo": "Risk Accepted by CEO",
            "risk_accepted_by_crp": "Risk Accepted by Chief Remote Pilot",
            "briefing_notes": "Briefing Notes",
            # Assignment and Crew labels
            "assigned_pilot": "Assigned Pilot",
            "crew_members": "Crew Members",
            # Additional Mission Details labels
            "estimated_duration": "Estimated Duration (Hours)",
            "weather_requirements": "Weather Requirements",
            "special_requirements": "Special Requirements",
            "notes": "Additional Notes",
        }

        help_texts = {
            "mission_id": "Unique mission identifier (auto-generated if left blank)",
            "name": "Short, descriptive name for the mission",
            "mission_type": "Type of RPA operation being conducted",
            "description": "Detailed description of mission objectives and requirements",
            "client": "Client organization requesting this mission",
            "mission_commander": "Staff member responsible for mission oversight",
            "status": "Current status of the mission",
            "priority": "Priority level for mission execution",
            "planned_start_date": "Planned date and time for mission commencement",
            "planned_end_date": "Planned date and time for mission completion",
            "actual_start_date": "Actual date and time mission started (if applicable)",
            "actual_end_date": "Actual date and time mission completed (if applicable)",
            "casa_authorization_required": "Check if mission requires specific CASA authorization",
            "casa_authorization_reference": "Reference number for CASA authorization or exemption",
            "risk_assessment_required": "Check if formal risk assessment is required",
            "jsa_required": "Check if Job Safety Assessment is required",
            "overall_risk_level": "Overall risk level from completed risk assessment",
            "risk_accepted_by_ceo": "High risk missions must be accepted by CEO",
            "risk_accepted_by_crp": "Medium/Low risk missions accepted by Chief Remote Pilot",
            "briefing_notes": "Additional notes and considerations for mission briefings",
            # Assignment and Crew help texts
            "assigned_pilot": "Primary pilot assigned to this mission",
            "crew_members": "Additional crew members assigned to this mission (hold Ctrl/Cmd to select multiple)",
            # Additional Mission Details help texts
            "estimated_duration": "Estimated mission duration in hours (e.g., 2.5 for 2 hours 30 minutes)",
            "weather_requirements": "Specific weather conditions required for this mission",
            "special_requirements": "Special equipment, permissions, or considerations required",
            "notes": "Additional notes and operational considerations",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make mission_id optional for auto-generation
        self.fields["mission_id"].required = False

        # Make actual dates optional initially
        self.fields["actual_start_date"].required = False
        self.fields["actual_end_date"].required = False

        # Make CASA authorization reference conditional
        self.fields["casa_authorization_reference"].required = False

        # Set default values for new missions (when no instance exists)
        if not self.instance.pk:
            self.fields["status"].initial = "planning"
            self.fields["priority"].initial = "medium"
            self.fields["risk_assessment_required"].initial = True
            self.fields["jsa_required"].initial = True
            self.fields["casa_authorization_required"].initial = False
            self.fields["risk_accepted_by_ceo"].initial = False
            self.fields["risk_accepted_by_crp"].initial = False

        # Make staff profile querysets more efficient
        from accounts.models import ClientProfile, StaffProfile

        staff_queryset = StaffProfile.objects.select_related("user").order_by(
            "user__first_name"
        )
        self.fields["mission_commander"].queryset = staff_queryset

        client_queryset = ClientProfile.objects.select_related("user").order_by(
            "user__first_name"
        )
        self.fields["client"].queryset = client_queryset

    def clean_mission_id(self):
        """Validate mission ID format and uniqueness"""
        mission_id = self.cleaned_data.get("mission_id", "").strip().upper()

        if mission_id:
            # Validate format
            import re

            if not re.match(r"^MSN-\d{4}-\d{6}$", mission_id):
                raise ValidationError("Mission ID must be in format MSN-YYYY-XXXXXX")

            # Check uniqueness (exclude current instance if updating)
            queryset = Mission.objects.filter(mission_id=mission_id)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise ValidationError("This Mission ID is already in use")

        return mission_id

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()

        planned_start = cleaned_data.get("planned_start_date")
        planned_end = cleaned_data.get("planned_end_date")
        actual_start = cleaned_data.get("actual_start_date")
        actual_end = cleaned_data.get("actual_end_date")

        # Validate planned dates
        if planned_start and planned_end and planned_end <= planned_start:
            raise ValidationError("Planned end date must be after start date")

        # Validate actual dates
        if actual_start and actual_end and actual_end <= actual_start:
            raise ValidationError("Actual end date must be after start date")

        # CASA authorization validation
        casa_required = cleaned_data.get("casa_authorization_required")
        casa_reference = cleaned_data.get("casa_authorization_reference")

        if casa_required and not casa_reference:
            raise ValidationError(
                "CASA authorization reference is required when authorization is needed"
            )

        return cleaned_data


class FlightLogForm(forms.ModelForm):
    """Form for creating and editing flight logs"""

    class Meta:
        model = FlightLog
        fields = [
            "aircraft_flight_plan",
            "drone_flight_plan",
            "takeoff_time",
            "landing_time",
            "flight_time",
            "maximum_altitude_achieved",
            "maximum_range_achieved",
            "pre_flight_battery_voltage",
            "post_flight_battery_voltage",
            "wind_speed_takeoff",
            "wind_direction_takeoff",
            "temperature_celsius",
            "visibility_meters",
            "log_entry_type",
            "objectives_achieved",
            "technical_issues",
            "weather_issues",
            "operational_notes",
            "lessons_learned",
            "pilot_performance_notes",
            "regulatory_compliance_notes",
            "data_collected",
            "file_references",
            "maintenance_required",
            "maintenance_notes",
        ]

        widgets = {
            "flight_plan": forms.Select(attrs={"class": "form-select"}),
            "takeoff_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "landing_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "flight_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "maximum_altitude_achieved": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "feet AGL",
                }
            ),
            "maximum_range_achieved": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "meters",
                }
            ),
            "pre_flight_battery_voltage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Volts",
                }
            ),
            "post_flight_battery_voltage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Volts",
                }
            ),
            "wind_speed_takeoff": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "Knots",
                }
            ),
            "wind_direction_takeoff": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "360",
                    "placeholder": "Degrees (0-360)",
                }
            ),
            "temperature_celsius": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "°C",
                }
            ),
            "visibility_meters": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "meters",
                }
            ),
            "log_entry_type": forms.Select(attrs={"class": "form-select"}),
            "objectives_achieved": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "technical_issues": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Any technical issues encountered",
                }
            ),
            "weather_issues": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Any weather-related issues",
                }
            ),
            "operational_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "General operational notes and observations",
                }
            ),
            "pilot_performance_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Notes on pilot performance (for training flights)",
                }
            ),
            "regulatory_compliance_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Notes on regulatory compliance during flight",
                }
            ),
            "data_collected": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Description of data/imagery collected",
                }
            ),
            "file_references": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "References to collected files, images, or data",
                }
            ),
            "lessons_learned": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Lessons learned from this flight",
                }
            ),
            "maintenance_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "maintenance_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Maintenance requirements or notes",
                }
            ),
        }

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()

        takeoff_time = cleaned_data.get("takeoff_time")
        landing_time = cleaned_data.get("landing_time")

        if takeoff_time and landing_time and landing_time <= takeoff_time:
            raise ValidationError("Landing time must be after takeoff time")

        return cleaned_data


class RiskRegisterForm(forms.ModelForm):
    """Form for creating and editing risk register entries"""

    class Meta:
        model = RiskRegister
        fields = [
            "reference_number",
            "mission",
            "date_entered",
            "hazard",
            "risk_description",
            "existing_controls",
            "initial_likelihood",
            "initial_consequence",
            "additional_controls",
            "residual_likelihood",
            "residual_consequence",
            "risk_owner",
            "review_due_date",
            "actions_required",
            "risk_accepted",
            "accepted_by",
            "accepted_date",
        ]

        widgets = {
            "reference_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Auto-generated if left blank",
                }
            ),
            "mission": forms.Select(attrs={"class": "form-select"}),
            "date_entered": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "hazard": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Description of the hazard",
                }
            ),
            "risk_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Detailed description of the risk",
                }
            ),
            "existing_controls": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Current controls in place to manage this risk",
                }
            ),
            "initial_likelihood": forms.Select(attrs={"class": "form-select"}),
            "initial_consequence": forms.Select(attrs={"class": "form-select"}),
            "additional_controls": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional controls to be implemented",
                }
            ),
            "residual_likelihood": forms.Select(attrs={"class": "form-select"}),
            "residual_consequence": forms.Select(attrs={"class": "form-select"}),
            "residual_risk_level": forms.Select(attrs={"class": "form-select"}),
            "acceptance_level": forms.Select(attrs={"class": "form-select"}),
            "accepted_by": forms.Select(attrs={"class": "form-select"}),
            "accepted_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "review_due_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "actions_required": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Actions required to mitigate risk",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make reference number optional for auto-generation
        self.fields["reference_number"].required = False

        # Make some fields optional
        self.fields["accepted_by"].required = False
        self.fields["accepted_date"].required = False
        self.fields["actions_required"].required = False


class JobSafetyAssessmentForm(forms.ModelForm):
    """Form for creating and editing Job Safety Assessments"""

    class Meta:
        model = JobSafetyAssessment
        fields = [
            "jsa_id",
            "mission",
            "related_aircraft_flight_plan",
            "related_drone_flight_plan",
            # "related_flight_plan" - REMOVED: Legacy field
            "sop_reference",
            "sop_step_number",
            "creation_context",
            "operation_type",
            "airspace_class",
            "flight_types",
            "airspace_hazards",
            "ground_hazards",
            "sop_adequate",
            "unmitigated_hazards",
            "preliminary_assessment_accurate",
            "assessment_changes",
            "additional_operating_restrictions",
            "official_authorization",
            "flight_authorized",
            "authorized_date",
            "approved_aircraft_types",
            "crp_approval_signature",
            "crp_approval_date",
            "rp_approval_signature",
            "rp_approval_date",
            "review_date",
        ]

        widgets = {
            "jsa_reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Auto-generated if left blank",
                }
            ),
            "mission": forms.Select(attrs={"class": "form-select"}),
            "assessment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "assessor": forms.Select(attrs={"class": "form-select"}),
            "job_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Detailed description of the job/task to be performed",
                }
            ),
            "location_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Description of work location and environment",
                }
            ),
            "equipment_required": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "List of equipment and tools required",
                }
            ),
            "personnel_required": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Personnel requirements and qualifications",
                }
            ),
            "identified_hazards": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "List of identified hazards and risks",
                }
            ),
            "risk_controls": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Risk control measures and mitigation strategies",
                }
            ),
            "emergency_procedures": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Emergency response procedures",
                }
            ),
            "ppe_required": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Personal protective equipment requirements",
                }
            ),
            "training_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Training requirements for personnel",
                }
            ),
            "environmental_considerations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Environmental factors and considerations",
                }
            ),
            "approval_status": forms.Select(attrs={"class": "form-select"}),
            "approved_by": forms.Select(attrs={"class": "form-select"}),
            "approval_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "review_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "title": "JSA Review Date for Compliance and Continuous Improvement",
                }
            ),
            "related_aircraft_flight_plan": forms.Select(
                attrs={
                    "class": "form-select",
                    "title": "Aircraft flight plan that triggered this JSA creation",
                }
            ),
            "related_drone_flight_plan": forms.Select(
                attrs={
                    "class": "form-select",
                    "title": "Drone flight plan that triggered this JSA creation",
                }
            ),
            # "related_flight_plan" widget removed - legacy field
            "sop_reference": forms.Select(
                attrs={
                    "class": "form-select",
                    "title": "Standard Operating Procedure that required this JSA",
                }
            ),
            "sop_step_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "title": "Specific SOP step number that triggered JSA creation",
                }
            ),
            "creation_context": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Detailed operational context (e.g., 'Created during Step 2 of Flight Operations SOP for Mission ABC123')",
                    "title": "Detailed description of why this JSA was created",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make JSA ID optional for auto-generation
        self.fields["jsa_id"].required = False

        # Make creation context fields optional initially
        self.fields["related_aircraft_flight_plan"].required = False
        self.fields["related_drone_flight_plan"].required = False
        self.fields["sop_reference"].required = False
        self.fields["sop_step_number"].required = False
        self.fields["creation_context"].required = False

        # Make approval fields optional initially
        self.fields["crp_approval_signature"].required = False
        self.fields["crp_approval_date"].required = False
        self.fields["rp_approval_signature"].required = False
        self.fields["rp_approval_date"].required = False
        self.fields["review_date"].required = False


class FlightPlanTypeSelectForm(forms.Form):
    """Form for selecting flight plan operation type"""

    OPERATION_TYPE_CHOICES = [
        ('', 'Select Operation Type'),
        ('aircraft', 'Aircraft Flight Plan'),
        ('drone', 'Drone/RPAS Flight Plan'),
    ]

    operation_type = forms.ChoiceField(
        choices=OPERATION_TYPE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'operation-type-select'}
        ),
        label="Operation Type",
        help_text="Select the type of flight operation to create a flight plan for",
    )

    mission = forms.ModelChoiceField(
        queryset=Mission.objects.all(), widget=forms.HiddenInput(), required=False
    )


class AircraftFlightPlanForm(forms.ModelForm):
    """Form for creating and editing aircraft flight plans"""

    class Meta:
        model = AircraftFlightPlan
        fields = [
            'mission',
            'aircraft',
            'pilot_in_command',
            'co_pilot',
            'flight_type',
            'flight_rules',
            'departure_airport',
            'arrival_airport',
            'alternate_airport',
            'route',
            'cruise_altitude',
            'planned_departure_time',
            'planned_arrival_time',
            'estimated_flight_time',
            'fuel_required',
            'payload_weight',
            'passenger_count',
            'weather_conditions',
            'weather_minimums',
            'special_instructions',
            'emergency_procedures',
            'notam_checked',
            'airspace_coordination_required',
            'airspace_coordination_reference',
            'atc_clearance',
        ]

        widgets = {
            'mission': forms.Select(attrs={'class': 'form-select'}),
            'aircraft': forms.Select(attrs={'class': 'form-select'}),
            'pilot_in_command': forms.Select(attrs={'class': 'form-select'}),
            'co_pilot': forms.Select(attrs={'class': 'form-select'}),
            'flight_type': forms.Select(attrs={'class': 'form-select'}),
            'flight_rules': forms.Select(attrs={'class': 'form-select'}),
            'departure_airport': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'YSSY',
                    'maxlength': 4,
                    'style': 'text-transform: uppercase;',
                }
            ),
            'arrival_airport': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'YMEL',
                    'maxlength': 4,
                    'style': 'text-transform: uppercase;',
                }
            ),
            'alternate_airport': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'YMML (optional)',
                    'maxlength': 4,
                    'style': 'text-transform: uppercase;',
                }
            ),
            'route': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter airways, waypoints, and routing',
                }
            ),
            'cruise_altitude': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '5500',
                    'min': 0,
                    'max': 50000,
                }
            ),
            'planned_departure_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'planned_arrival_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'estimated_flight_time': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),
            'fuel_required': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': '250.00', 'step': '0.01'}
            ),
            'payload_weight': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': '450.00', 'step': '0.01'}
            ),
            'passenger_count': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'max': 20}
            ),
            'weather_conditions': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Current weather conditions and forecast',
                }
            ),
            'weather_minimums': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Minimum weather conditions required',
                }
            ),
            'special_instructions': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Special operational instructions',
                }
            ),
            'emergency_procedures': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Emergency procedures specific to this flight',
                }
            ),
            'airspace_coordination_reference': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ATC clearance or coordination reference',
                }
            ),
            'atc_clearance': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'ATC clearance details',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make some fields optional initially
        self.fields['co_pilot'].required = False
        self.fields['alternate_airport'].required = False
        self.fields['planned_arrival_time'].required = False
        self.fields['weather_conditions'].required = False
        self.fields['special_instructions'].required = False
        self.fields['airspace_coordination_reference'].required = False
        self.fields['atc_clearance'].required = False


class DroneFlightPlanForm(forms.ModelForm):
    """Form for creating and editing drone flight plans"""

    class Meta:
        model = DroneFlightPlan
        fields = [
            'mission',
            'drone',
            'remote_pilot',
            'visual_observer',
            'flight_type',
            'takeoff_location',
            'landing_location',
            'maximum_altitude_agl',
            'maximum_range_from_pilot',
            'planned_departure_time',
            'planned_arrival_time',
            'estimated_flight_time',
            'battery_capacity',
            'estimated_battery_consumption',
            'payload_description',
            'weather_conditions',
            'weather_minimums',
            'special_instructions',
            'emergency_procedures',
            'lost_link_procedures',
            'casa_approval_number',
            'airspace_approval',
            'notam_checked',
            'airspace_coordination_required',
            'airspace_coordination_reference',
            'no_fly_zones_checked',
            'waypoints',
            'autonomous_mode',
            'return_to_home_altitude',
        ]

        widgets = {
            'mission': forms.Select(attrs={'class': 'form-select'}),
            'drone': forms.Select(attrs={'class': 'form-select'}),
            'remote_pilot': forms.Select(attrs={'class': 'form-select'}),
            'visual_observer': forms.Select(attrs={'class': 'form-select'}),
            'flight_type': forms.Select(attrs={'class': 'form-select'}),
            'takeoff_location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Describe takeoff location',
                }
            ),
            'landing_location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Describe landing location',
                }
            ),
            'maximum_altitude_agl': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '120',
                    'min': 1,
                    'max': 400,
                }
            ),
            'maximum_range_from_pilot': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '500',
                    'min': 1,
                    'max': 500,
                }
            ),
            'planned_departure_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'planned_arrival_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'estimated_flight_time': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),
            'battery_capacity': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': '5000', 'step': '1'}
            ),
            'estimated_battery_consumption': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '75.00',
                    'step': '0.01',
                    'min': 0,
                    'max': 100,
                }
            ),
            'payload_description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Describe payload and equipment',
                }
            ),
            'weather_conditions': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Current weather conditions and forecast',
                }
            ),
            'weather_minimums': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Minimum weather conditions required',
                }
            ),
            'special_instructions': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Special operational instructions',
                }
            ),
            'emergency_procedures': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Emergency procedures specific to this flight',
                }
            ),
            'lost_link_procedures': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Procedures if communication link is lost',
                }
            ),
            'casa_approval_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ReOC or approval number',
                }
            ),
            'airspace_approval': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Airspace approval reference',
                }
            ),
            'airspace_coordination_reference': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ATC coordination reference',
                }
            ),
            'waypoints': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'GPS waypoints in JSON format. Example: [{"lat": -33.8688, "lng": 151.2093, "alt": 100}, {"lat": -33.8700, "lng": 151.2100, "alt": 100}] or leave empty []',
                }
            ),
            'return_to_home_altitude': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '100',
                    'min': 50,
                    'max': 400,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make some fields optional initially
        self.fields['visual_observer'].required = False
        self.fields['planned_arrival_time'].required = False
        self.fields['weather_conditions'].required = False
        self.fields['special_instructions'].required = False
        self.fields['casa_approval_number'].required = False
        self.fields['airspace_approval'].required = False
        self.fields['airspace_coordination_reference'].required = False

        # Make fields with model defaults optional
        self.fields['waypoints'].required = False
        self.fields['return_to_home_altitude'].required = False

        # Set defaults for JSON and numeric fields that have model defaults
        if not self.instance.pk:  # Only for new instances
            self.initial['waypoints'] = []
            self.initial['return_to_home_altitude'] = 100
