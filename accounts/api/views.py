from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from ..models import (
    ClientProfile,
    CompanyContactDetails,
    KeyPersonnel,
    OperatorCertificate,
    PilotProfile,
    StaffProfile,
)

from .serializers import (
    CustomUserSerializer,
    StaffProfileSerializer,
    StaffProfileDetailSerializer,
    PilotProfileSerializer,
    PilotProfileDetailSerializer,
    ClientProfileSerializer,
    OperatorCertificateSerializer,
    CompanyContactDetailsSerializer,
    KeyPersonnelSerializer,
    UserSummarySerializer,
)

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for CustomUser model
    Provides CRUD operations for user management
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'last_name', 'date_joined']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        """Use summary serializer for list view"""
        if self.action == 'list':
            return UserSummarySerializer
        return CustomUserSerializer

    def get_permissions(self):
        """
        Different permissions for different actions
        """
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        """Set password for user"""
        user = self.get_object()
        password = request.data.get('password')
        if password:
            user.set_password(password)
            user.save()
            return Response({'message': 'Password updated successfully'})
        return Response({'error': 'Password required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class StaffProfileViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for StaffProfile model
    """
    queryset = StaffProfile.objects.select_related('user').all()
    serializer_class = StaffProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'position_title']
    ordering_fields = ['user__first_name', 'user__last_name', 'hire_date']
    ordering = ['user__first_name']

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return StaffProfileDetailSerializer
        return StaffProfileSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active staff members"""
        active_staff = self.queryset.filter(is_active=True, user__is_active=True)
        serializer = self.get_serializer(active_staff, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get staff grouped by department"""
        departments = {}
        for staff in self.queryset.filter(is_active=True):
            dept = staff.department or 'Unassigned'
            if dept not in departments:
                departments[dept] = []
            departments[dept].append(self.get_serializer(staff).data)
        return Response(departments)


class PilotProfileViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for PilotProfile model
    """
    queryset = PilotProfile.objects.select_related('user').all()
    serializer_class = PilotProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['license_type', 'availability_status']
    search_fields = ['user__first_name', 'user__last_name', 'license_number']
    ordering_fields = ['user__first_name', 'user__last_name', 'total_flight_hours']
    ordering = ['user__first_name']

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return PilotProfileDetailSerializer
        return PilotProfileSerializer

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available pilots"""
        available_pilots = self.queryset.filter(
            availability_status='available',
            user__is_active=True
        )
        serializer = self.get_serializer(available_pilots, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring_licenses(self, request):
        """Get pilots with licenses expiring soon"""
        from datetime import date, timedelta
        
        thirty_days = date.today() + timedelta(days=30)
        expiring = self.queryset.filter(
            license_expiry_date__lte=thirty_days,
            license_expiry_date__gte=date.today()
        )
        serializer = self.get_serializer(expiring, many=True)
        return Response(serializer.data)


class ClientProfileViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for ClientProfile model
    """
    queryset = ClientProfile.objects.select_related('user').all()
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'preferred_communication']
    search_fields = ['user__first_name', 'user__last_name', 'company_name', 'abn']
    ordering_fields = ['user__first_name', 'company_name', 'registration_date']
    ordering = ['company_name']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active clients"""
        active_clients = self.queryset.filter(status='active', user__is_active=True)
        serializer = self.get_serializer(active_clients, many=True)
        return Response(serializer.data)


class OperatorCertificateViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for OperatorCertificate model
    """
    queryset = OperatorCertificate.objects.all()
    serializer_class = OperatorCertificateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'certificate_type']
    search_fields = ['reoc_number', 'company_name', 'casa_operator_number']
    ordering_fields = ['reoc_number', 'company_name', 'issue_date', 'expiry_date']
    ordering = ['-issue_date']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active certificates"""
        active_certs = self.queryset.filter(status='active')
        serializer = self.get_serializer(active_certs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        """Get certificates expiring within 30 days"""
        from datetime import date, timedelta
        
        thirty_days = date.today() + timedelta(days=30)
        expiring = self.queryset.filter(
            expiry_date__lte=thirty_days,
            expiry_date__gte=date.today(),
            status='active'
        )
        serializer = self.get_serializer(expiring, many=True)
        return Response(serializer.data)


class CompanyContactDetailsViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for CompanyContactDetails singleton model
    Only allows retrieve and update operations
    """
    serializer_class = CompanyContactDetailsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Always return the singleton instance"""
        return CompanyContactDetails.objects.all()
    
    def get_object(self):
        """Get or create the singleton instance"""
        return CompanyContactDetails.get_instance()
    
    def list(self, request):
        """Return the singleton instance as a single item"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request):
        """Don't allow creation - redirect to update"""
        return Response(
            {'message': 'Company details already exist. Use PUT to update.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, pk=None):
        """Don't allow deletion"""
        return Response(
            {'message': 'Company details cannot be deleted.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class KeyPersonnelViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for KeyPersonnel singleton model
    Only allows retrieve and update operations
    """
    serializer_class = KeyPersonnelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Always return the singleton instance"""
        return KeyPersonnel.objects.all()
    
    def get_object(self):
        """Get or create the singleton instance"""
        return KeyPersonnel.load()
    
    def list(self, request):
        """Return the singleton instance as a single item"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request):
        """Don't allow creation - redirect to update"""
        return Response(
            {'message': 'Key Personnel record already exists. Use PUT to update.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, pk=None):
        """Don't allow deletion"""
        return Response(
            {'message': 'Key Personnel record cannot be deleted.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=False, methods=['get'])
    def compliance_status(self, request):
        """Get CASA compliance status"""
        personnel = self.get_object()
        return Response({
            'casa_compliant': personnel.is_casa_compliant(),
            'vacant_positions': personnel.get_vacant_positions(),
            'personnel_summary': personnel.get_personnel_summary()
        })
    
    @action(detail=False, methods=['get'])
    def available_personnel(self, request):
        """Get available staff and pilots for assignment"""
        return Response({
            'pilots': PilotProfileSerializer(
                PilotProfile.objects.filter(user__is_active=True), 
                many=True
            ).data,
            'staff': StaffProfileSerializer(
                StaffProfile.objects.filter(is_active=True, user__is_active=True), 
                many=True
            ).data
        })