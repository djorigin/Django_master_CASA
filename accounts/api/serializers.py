from django.contrib.auth import get_user_model

from rest_framework import serializers

from ..models import (
    ClientProfile,
    CompanyContactDetails,
    CustomUser,
    KeyPersonnel,
    OperatorCertificate,
    PilotProfile,
    StaffProfile,
)

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model"""

    full_name = serializers.CharField(source="get_full_name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "date_joined",
            "last_login",
            "full_name",
            "role_display",
        ]
        read_only_fields = ["date_joined", "last_login"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Create user with encrypted password"""
        password = validated_data.pop("password", None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user with encrypted password"""
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class StaffProfileSerializer(serializers.ModelSerializer):
    """Serializer for StaffProfile model"""

    user = CustomUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            "id",
            "user",
            "user_id",
            "position_title",
            "department",
            "employee_id",
            "hire_date",
            "is_active",
            "contact_number",
            "address",
            "photo_id",
        ]


class PilotProfileSerializer(serializers.ModelSerializer):
    """Serializer for PilotProfile model"""

    user = CustomUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PilotProfile
        fields = [
            "id",
            "user",
            "user_id",
            "license_number",
            "license_type",
            "license_expiry_date",
            "medical_certificate_expiry",
            "total_flight_hours",
            "drone_flight_hours",
            "availability_status",
            "contact_number",
            "emergency_contact_name",
            "emergency_contact_number",
            "address",
            "photo_id",
        ]


class ClientProfileSerializer(serializers.ModelSerializer):
    """Serializer for ClientProfile model"""

    user = CustomUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            "id",
            "user",
            "user_id",
            "company_name",
            "abn",
            "contact_number",
            "billing_address",
            "service_address",
            "preferred_communication",
            "status",
            "registration_date",
            "notes",
            "photo_id",
        ]


class OperatorCertificateSerializer(serializers.ModelSerializer):
    """Serializer for OperatorCertificate model"""

    class Meta:
        model = OperatorCertificate
        fields = [
            "id",
            "reoc_number",
            "certificate_type",
            "company_name",
            "contact_email",
            "issue_date",
            "expiry_date",
            "status",
            "casa_operator_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class CompanyContactDetailsSerializer(serializers.ModelSerializer):
    """Serializer for CompanyContactDetails singleton model"""

    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = CompanyContactDetails
        fields = [
            "id",
            "legal_entity_name",
            "trading_name",
            "display_name",
            "registered_office_address",
            "arn",
            "abn",
            "operational_hq_address",
            "operational_hq_phone",
            "operational_hq_email",
            "organizational_overview",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class KeyPersonnelSerializer(serializers.ModelSerializer):
    """Serializer for KeyPersonnel singleton model"""

    chief_remote_pilot = PilotProfileSerializer(read_only=True)
    chief_remote_pilot_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    maintenance_controller = StaffProfileSerializer(read_only=True)
    maintenance_controller_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    ceo = StaffProfileSerializer(read_only=True)
    ceo_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    # Additional computed fields
    personnel_summary = serializers.SerializerMethodField()
    vacant_positions = serializers.SerializerMethodField()
    casa_compliant = serializers.SerializerMethodField()

    class Meta:
        model = KeyPersonnel
        fields = [
            "id",
            "chief_remote_pilot",
            "chief_remote_pilot_id",
            "chief_remote_pilot_approved_date",
            "maintenance_controller",
            "maintenance_controller_id",
            "maintenance_controller_approved_date",
            "ceo",
            "ceo_id",
            "ceo_approved_date",
            "personnel_summary",
            "vacant_positions",
            "casa_compliant",
            "created_at",
            "last_updated",
        ]
        read_only_fields = ["created_at", "last_updated"]

    def get_personnel_summary(self, obj):
        """Get personnel summary from model method"""
        return obj.get_personnel_summary()

    def get_vacant_positions(self, obj):
        """Get vacant positions from model method"""
        return obj.get_vacant_positions()

    def get_casa_compliant(self, obj):
        """Get CASA compliance status from model method"""
        return obj.is_casa_compliant()

    def validate(self, data):
        """Validate that same person doesn't hold multiple positions"""
        maintenance_controller_id = data.get("maintenance_controller_id")
        ceo_id = data.get("ceo_id")

        if maintenance_controller_id and ceo_id and maintenance_controller_id == ceo_id:
            raise serializers.ValidationError(
                "The same person cannot hold both Maintenance Controller and CEO positions simultaneously."
            )

        return data


# Nested serializers for detailed views
class StaffProfileDetailSerializer(StaffProfileSerializer):
    """Detailed staff profile with additional computed fields"""

    key_positions = serializers.SerializerMethodField()

    class Meta(StaffProfileSerializer.Meta):
        fields = StaffProfileSerializer.Meta.fields + ["key_positions"]

    def get_key_positions(self, obj):
        """Get key positions held by this staff member"""
        positions = []
        try:
            personnel = KeyPersonnel.load()
            if personnel.maintenance_controller == obj:
                positions.append("Maintenance Controller")
            if personnel.ceo == obj:
                positions.append("CEO")
        except:
            pass
        return positions


class PilotProfileDetailSerializer(PilotProfileSerializer):
    """Detailed pilot profile with additional computed fields"""

    key_positions = serializers.SerializerMethodField()

    class Meta(PilotProfileSerializer.Meta):
        fields = PilotProfileSerializer.Meta.fields + ["key_positions"]

    def get_key_positions(self, obj):
        """Get key positions held by this pilot"""
        positions = []
        try:
            personnel = KeyPersonnel.load()
            if personnel.chief_remote_pilot == obj:
                positions.append("Chief Remote Pilot")
        except:
            pass
        return positions


# Summary serializers for list views
class UserSummarySerializer(serializers.ModelSerializer):
    """Lightweight user serializer for list views"""

    full_name = serializers.CharField(source="get_full_name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "role_display",
            "is_active",
            "date_joined",
        ]
