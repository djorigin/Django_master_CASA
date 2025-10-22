from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from accounts.models import ClientProfile, CustomUser
from .models import AircraftType, Aircraft


class AircraftTypeModelTest(TestCase):
    """Test cases for AircraftType model CASA compliance"""
    
    def setUp(self):
        """Set up test data"""
        pass
    
    def test_excluded_category_validation(self):
        """Test excluded category aircraft validation per Part 101.073"""
        # Valid excluded category aircraft
        aircraft_type = AircraftType(
            name="DJI Mini 2",
            manufacturer="DJI",
            model="Mini 2",
            category='excluded',
            operation_type='recreational',
            maximum_takeoff_weight=Decimal('0.249'),  # 249g
            maximum_operating_height=120,  # 120ft
            maximum_speed=36
        )
        
        # Should not raise validation error
        try:
            aircraft_type.clean()
        except ValidationError:
            self.fail("Valid excluded category aircraft should not raise ValidationError")
        
        # Test invalid weight (over 25kg for excluded category)
        aircraft_type.maximum_takeoff_weight = Decimal('26.0')
        with self.assertRaises(ValidationError):
            aircraft_type.clean()
    
    def test_micro_rpa_validation(self):
        """Test micro RPA category validation"""
        aircraft_type = AircraftType(
            name="Micro Drone",
            manufacturer="Test Manufacturer",
            model="Micro 1",
            category='micro',
            operation_type='recreational',
            maximum_takeoff_weight=Decimal('0.3'),  # 300g - invalid for micro
            maximum_operating_height=120,
            maximum_speed=20
        )
        
        with self.assertRaises(ValidationError):
            aircraft_type.clean()
    
    def test_commercial_medium_aircraft_certificate_requirement(self):
        """Test that commercial medium/large aircraft require CASA certificate"""
        aircraft_type = AircraftType(
            name="Commercial Medium",
            manufacturer="Commercial Corp",
            model="Medium 100",
            category='medium',
            operation_type='commercial',
            maximum_takeoff_weight=Decimal('50.0'),
            maximum_operating_height=400,
            casa_type_certificate=""  # Missing certificate
        )
        
        with self.assertRaises(ValidationError):
            aircraft_type.clean()
    
    def test_string_representation(self):
        """Test model string representation"""
        aircraft_type = AircraftType(
            name="Test Aircraft",
            manufacturer="Test Mfg",
            model="Model X",
            category='small',
            operation_type='commercial',
            maximum_takeoff_weight=Decimal('10.0'),
            maximum_operating_height=400
        )
        
        expected = "Test Mfg Model X (Small RPA (>250g ≤25kg))"
        self.assertEqual(str(aircraft_type), expected)


class AircraftModelTest(TestCase):
    """Test cases for Aircraft model"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user and client profile
        self.user = CustomUser.objects.create_user(
            username='testclient',
            email='test@example.com',
            password='testpass123',
            role='client'
        )
        
        self.client_profile = ClientProfile.objects.create(
            user=self.user,
            company_name='Test Aviation Company',
            contact_person='John Doe',
            phone_number='+61412345678',
            address='123 Test St, Sydney NSW 2000'
        )
        
        # Create test aircraft type
        self.aircraft_type = AircraftType.objects.create(
            name="Test Aircraft Type",
            manufacturer="Test Manufacturer",
            model="Test Model",
            category='small',
            operation_type='commercial',
            maximum_takeoff_weight=Decimal('15.0'),
            maximum_operating_height=400,
            casa_type_certificate="TC-TEST-001"
        )
    
    def test_aircraft_creation(self):
        """Test basic aircraft creation"""
        aircraft = Aircraft.objects.create(
            registration_mark='TEST-001',
            aircraft_type=self.aircraft_type,
            owner=self.client_profile,
            serial_number='SN123456',
            year_manufactured=2023,
            airworthiness_valid_until=date.today() + timedelta(days=365),
            insurance_valid_until=date.today() + timedelta(days=180)
        )
        
        self.assertEqual(aircraft.registration_mark, 'TEST-001')
        self.assertEqual(aircraft.owner, self.client_profile)
        self.assertTrue(aircraft.is_airworthy)
        self.assertTrue(aircraft.is_insured)
    
    def test_operational_status_properties(self):
        """Test aircraft operational status properties"""
        # Create operational aircraft
        aircraft = Aircraft.objects.create(
            registration_mark='OP-001',
            aircraft_type=self.aircraft_type,
            owner=self.client_profile,
            serial_number='SN789012',
            year_manufactured=2023,
            status='registered',
            airworthiness_valid_until=date.today() + timedelta(days=365),
            insurance_valid_until=date.today() + timedelta(days=180),
            next_maintenance_due=date.today() + timedelta(days=30)
        )
        
        self.assertTrue(aircraft.is_operational)
        self.assertEqual(aircraft.maintenance_status, 'current')
        
        # Test maintenance due soon
        aircraft.next_maintenance_due = date.today() + timedelta(days=5)
        aircraft.save()
        self.assertEqual(aircraft.maintenance_status, 'due_soon')
        
        # Test overdue maintenance
        aircraft.next_maintenance_due = date.today() - timedelta(days=1)
        aircraft.save()
        self.assertEqual(aircraft.maintenance_status, 'overdue')
        self.assertFalse(aircraft.is_operational)
    
    def test_commercial_operator_validation(self):
        """Test that commercial aircraft must have operator"""
        aircraft = Aircraft(
            registration_mark='COM-001',
            aircraft_type=self.aircraft_type,
            owner=self.client_profile,
            serial_number='SN345678',
            year_manufactured=2023,
            operator=None  # Missing operator for commercial aircraft
        )
        
        with self.assertRaises(ValidationError):
            aircraft.clean()
    
    def test_string_representation(self):
        """Test aircraft string representation"""
        aircraft = Aircraft(
            registration_mark='REP-001',
            aircraft_type=self.aircraft_type,
            owner=self.client_profile,
            serial_number='SN901234',
            year_manufactured=2023
        )
        
        expected = "REP-001 - Test Manufacturer Test Model"
        self.assertEqual(str(aircraft), expected)
