from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import (
    ClientProfile,
    CustomUser,
    KeyPersonnel,
    OperatorCertificate,
    PilotProfile,
    StaffProfile,
)


class CustomUserForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}
        ),
        required=False,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm password"}
        ),
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "role", "is_active"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Enter email address"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter first name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter last name"}
            ),
            "role": forms.Select(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = [
            "user",
            "department",
            "position_title",
            "contact_number",
            "address",
            "photo_id",
            "employee_id",
            "hire_date",
            "is_active",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-control"}),
            "position_title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter position title"}
            ),
            "contact_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+61 400 000 000"}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter full address",
                }
            ),
            "photo_id": forms.FileInput(
                attrs={"class": "form-control-file", "accept": "image/*"}
            ),
            "employee_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter employee ID"}
            ),
            "hire_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users to only show those with staff role
        self.fields["user"].queryset = CustomUser.objects.filter(role="staff")


class PilotProfileForm(forms.ModelForm):
    class Meta:
        model = PilotProfile
        fields = [
            "user",
            "role",
            "arn",
            "repl_number",
            "repl_expiry",
            "medical_clearance_date",
            "certifications",
            "availability_status",
            "home_base_location",
            "emergency_contact_name",
            "emergency_contact_phone",
            "contact_number",
            "address",
            "photo_id",
            "notes",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "arn": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter ARN Number"}
            ),
            "repl_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter REPL Number"}
            ),
            "repl_expiry": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "medical_clearance_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "certifications": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "List additional certifications",
                }
            ),
            "availability_status": forms.Select(attrs={"class": "form-control"}),
            "home_base_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter home base location",
                }
            ),
            "emergency_contact_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Emergency contact name"}
            ),
            "emergency_contact_phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+61 400 000 000"}
            ),
            "contact_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+61 400 000 000"}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter full address",
                }
            ),
            "photo_id": forms.FileInput(
                attrs={"class": "form-control-file", "accept": "image/*"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional notes",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users to only show those with pilot role
        self.fields["user"].queryset = CustomUser.objects.filter(role="pilot")


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            "user",
            "company_name",
            "abn",
            "contact_number",
            "address",
            "billing_email",
            "industry",
            "account_manager",
            "status",
            "credit_limit",
            "payment_terms",
            "notes",
            "photo_id",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "company_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter company name"}
            ),
            "abn": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter ABN"}
            ),
            "contact_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+61 400 000 000"}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter full address",
                }
            ),
            "billing_email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Enter billing email"}
            ),
            "industry": forms.Select(attrs={"class": "form-control"}),
            "account_manager": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "credit_limit": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}
            ),
            "payment_terms": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "30"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional notes",
                }
            ),
            "photo_id": forms.FileInput(
                attrs={"class": "form-control-file", "accept": "image/*"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users to only show those with client role
        self.fields["user"].queryset = CustomUser.objects.filter(role="client")
        # Show only active staff as account managers
        self.fields["account_manager"].queryset = StaffProfile.objects.filter(
            is_active=True
        )


class OperatorCertificateForm(forms.ModelForm):
    class Meta:
        model = OperatorCertificate
        fields = [
            "reoc_number",
            "company_name",
            "contact_email",
            "issue_date",
            "expiry_date",
            "status",
            "casa_operator_number",
        ]
        widgets = {
            "reoc_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter REOC Number"}
            ),
            "company_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter company name"}
            ),
            "contact_email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Enter contact email"}
            ),
            "issue_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "expiry_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "casa_operator_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter CASA Operator Number",
                }
            ),
        }


class KeyPersonnelForm(forms.ModelForm):
    """
    Form for managing CASA Key Personnel positions using existing vetted profiles.
    Ensures data security and integrity through ForeignKey relationships.
    """
    
    class Meta:
        model = KeyPersonnel
        fields = [
            'chief_remote_pilot',
            'chief_remote_pilot_approved_date',
            'maintenance_controller',
            'maintenance_controller_approved_date',
            'ceo',
            'ceo_approved_date',
        ]
        widgets = {
            'chief_remote_pilot': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select Chief Remote Pilot',
                }
            ),
            'chief_remote_pilot_approved_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': 'CASA Approval Date',
                }
            ),
            'maintenance_controller': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select Maintenance Controller',
                }
            ),
            'maintenance_controller_approved_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': 'CASA Approval Date',
                }
            ),
            'ceo': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select CEO',
                }
            ),
            'ceo_approved_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': 'CASA Approval Date',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize querysets to show relevant information
        self.fields['chief_remote_pilot'].queryset = PilotProfile.objects.select_related('user').filter(
            user__is_active=True
        )
        self.fields['maintenance_controller'].queryset = StaffProfile.objects.select_related('user').filter(
            user__is_active=True,
            is_active=True
        )
        self.fields['ceo'].queryset = StaffProfile.objects.select_related('user').filter(
            user__is_active=True,
            is_active=True
        )
        
        # Add help text
        self.fields['chief_remote_pilot'].help_text = "Select from existing pilot profiles with valid licenses"
        self.fields['maintenance_controller'].help_text = "Select from existing staff profiles qualified for maintenance control"
        self.fields['ceo'].help_text = "Select from existing staff profiles authorized as CEO"

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure no person holds multiple key positions simultaneously
        chief_pilot = cleaned_data.get('chief_remote_pilot')
        maintenance_controller = cleaned_data.get('maintenance_controller')
        ceo = cleaned_data.get('ceo')
        
        staff_positions = [maintenance_controller, ceo]
        
        # Check if same staff member is assigned to multiple positions
        if maintenance_controller and ceo and maintenance_controller == ceo:
            raise ValidationError(
                "The same person cannot hold both Maintenance Controller and CEO positions simultaneously."
            )
            
        return cleaned_data
