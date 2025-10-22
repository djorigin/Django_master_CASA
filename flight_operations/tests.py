from datetime import datetime, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounts.models import ClientProfile, CustomUser, PilotProfile, StaffProfile
from aircraft.models import Aircraft, AircraftType

from .models import FlightLog, FlightPlan, Mission


class MissionModelTest(TestCase):
    """Test cases for Mission model"""

    def setUp(self):
        """Set up test data"""
        # Create test users
        self.client_user = CustomUser.objects.create_user(
            username="testclient",
            email="client@test.com",
            password="test123",
            role="client",
        )

        self.staff_user = CustomUser.objects.create_user(
            username="teststaff",
            email="staff@test.com",
            password="test123",
            role="staff",
        )

        # Create profiles
        self.client_profile = ClientProfile.objects.create(
            user=self.client_user,
            company_name="Test Aviation Company",
            contact_person="John Client",
            phone_number="+61412345678",
            address="123 Test St, Sydney NSW 2000",
        )

        self.staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            position="Mission Commander",
            employee_id="EMP001",
            phone_number="+61412345679",
            emergency_contact="Jane Emergency",
            emergency_phone="+61412345680",
        )

    def test_mission_creation(self):
        """Test basic mission creation"""
        mission = Mission.objects.create(
            name="Test Mission",
            mission_type="commercial",
            description="Test mission description",
            client=self.client_profile,
            mission_commander=self.staff_profile,
            planned_start_date=timezone.now() + timedelta(days=1),
            planned_end_date=timezone.now() + timedelta(days=2),
        )

        self.assertEqual(mission.name, "Test Mission")
        self.assertEqual(mission.client, self.client_profile)
        self.assertTrue(mission.mission_id.startswith("MSN-"))

    def test_mission_validation(self):
        """Test mission date validation"""
        mission = Mission(
            name="Invalid Mission",
            mission_type="commercial",
            description="Test mission",
            client=self.client_profile,
            mission_commander=self.staff_profile,
            planned_start_date=timezone.now() + timedelta(days=2),
            planned_end_date=timezone.now()
            + timedelta(days=1),  # Invalid: before start
        )

        with self.assertRaises(ValidationError):
            mission.clean()

    def test_mission_properties(self):
        """Test mission property methods"""
        mission = Mission.objects.create(
            name="Active Mission",
            mission_type="commercial",
            description="Test mission",
            client=self.client_profile,
            mission_commander=self.staff_profile,
            status="active",
            planned_start_date=timezone.now() + timedelta(days=1),
            planned_end_date=timezone.now() + timedelta(days=2),
        )

        self.assertTrue(mission.is_active)
        self.assertIsNotNone(mission.duration_planned)


class FlightPlanModelTest(TestCase):
    """Test cases for FlightPlan model"""

    def setUp(self):
        """Set up test data"""
        # Create test users and profiles
        self.client_user = CustomUser.objects.create_user(
            username="testclient",
            email="client@test.com",
            password="test123",
            role="client",
        )

        self.pilot_user = CustomUser.objects.create_user(
            username="testpilot",
            email="pilot@test.com",
            password="test123",
            role="pilot",
        )

        self.staff_user = CustomUser.objects.create_user(
            username="teststaff",
            email="staff@test.com",
            password="test123",
            role="staff",
        )

        self.client_profile = ClientProfile.objects.create(
            user=self.client_user,
            company_name="Test Aviation Company",
            contact_person="John Client",
            phone_number="+61412345678",
            address="123 Test St, Sydney NSW 2000",
        )

        self.pilot_profile = PilotProfile.objects.create(
            user=self.pilot_user,
            license_number="RPL001",
            license_type="reoc",
            medical_certificate_expiry=timezone.now().date() + timedelta(days=365),
            flight_review_expiry=timezone.now().date() + timedelta(days=180),
            total_flight_hours=Decimal("150.5"),
        )

        self.staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            position="Mission Commander",
            employee_id="EMP001",
            phone_number="+61412345679",
            emergency_contact="Jane Emergency",
            emergency_phone="+61412345680",
        )

        # Create aircraft type and aircraft
        self.aircraft_type = AircraftType.objects.create(
            name="Test Aircraft Type",
            manufacturer="Test Manufacturer",
            model="Test Model",
            category="small",
            operation_type="commercial",
            maximum_takeoff_weight=Decimal("15.0"),
            maximum_operating_height=400,
        )

        self.aircraft = Aircraft.objects.create(
            registration_mark="TEST-001",
            aircraft_type=self.aircraft_type,
            owner=self.client_profile,
            serial_number="SN123456",
            year_manufactured=2023,
            status="registered",
        )

        # Create mission
        self.mission = Mission.objects.create(
            name="Test Mission",
            mission_type="commercial",
            description="Test mission",
            client=self.client_profile,
            mission_commander=self.staff_profile,
            planned_start_date=timezone.now() + timedelta(days=1),
            planned_end_date=timezone.now() + timedelta(days=2),
        )

    def test_flight_plan_creation(self):
        """Test basic flight plan creation"""
        flight_plan = FlightPlan.objects.create(
            mission=self.mission,
            aircraft=self.aircraft,
            pilot_in_command=self.pilot_profile,
            flight_type="line_of_sight",
            departure_location="Test Airfield",
            departure_latitude=Decimal("-33.946910"),
            departure_longitude=Decimal("151.177002"),
            planned_altitude_agl=120,
            maximum_range_from_pilot=500,
            planned_departure_time=timezone.now() + timedelta(hours=2),
            estimated_flight_time=timedelta(minutes=30),
            weather_minimums="VMC, visibility >3km, wind <15kts",
            planned_weather_check_time=timezone.now() + timedelta(hours=1),
            emergency_procedures="Land immediately if emergency",
            lost_link_procedures="Return to home point",
        )

        self.assertEqual(flight_plan.aircraft, self.aircraft)
        self.assertEqual(flight_plan.pilot_in_command, self.pilot_profile)
        self.assertTrue(flight_plan.flight_plan_id.startswith("FPL-"))

    def test_flight_plan_validation(self):
        """Test flight plan coordinate validation"""
        flight_plan = FlightPlan(
            mission=self.mission,
            aircraft=self.aircraft,
            pilot_in_command=self.pilot_profile,
            flight_type="line_of_sight",
            departure_location="Test Location",
            departure_latitude=Decimal("91.0"),  # Invalid latitude
            departure_longitude=Decimal("151.0"),
            planned_altitude_agl=120,
            maximum_range_from_pilot=500,
            planned_departure_time=timezone.now() + timedelta(hours=2),
            estimated_flight_time=timedelta(minutes=30),
            weather_minimums="VMC",
            planned_weather_check_time=timezone.now() + timedelta(hours=1),
            emergency_procedures="Emergency",
            lost_link_procedures="Lost link",
        )

        with self.assertRaises(ValidationError):
            flight_plan.clean()

    def test_vlos_validation(self):
        """Test VLOS altitude and range validation"""
        flight_plan = FlightPlan(
            mission=self.mission,
            aircraft=self.aircraft,
            pilot_in_command=self.pilot_profile,
            flight_type="line_of_sight",
            departure_location="Test Location",
            departure_latitude=Decimal("-33.946910"),
            departure_longitude=Decimal("151.177002"),
            planned_altitude_agl=150,  # Over typical VLOS limit
            maximum_range_from_pilot=600,  # Over VLOS limit
            planned_departure_time=timezone.now() + timedelta(hours=2),
            estimated_flight_time=timedelta(minutes=30),
            weather_minimums="VMC",
            planned_weather_check_time=timezone.now() + timedelta(hours=1),
            emergency_procedures="Emergency",
            lost_link_procedures="Lost link",
        )

        with self.assertRaises(ValidationError):
            flight_plan.clean()


class FlightLogModelTest(TestCase):
    """Test cases for FlightLog model"""

    def setUp(self):
        """Set up test data similar to FlightPlan test"""
        # Create all necessary test data (users, profiles, aircraft, mission, flight plan)
        self.client_user = CustomUser.objects.create_user(
            username="testclient",
            email="client@test.com",
            password="test123",
            role="client",
        )

        self.pilot_user = CustomUser.objects.create_user(
            username="testpilot",
            email="pilot@test.com",
            password="test123",
            role="pilot",
        )

        self.staff_user = CustomUser.objects.create_user(
            username="teststaff",
            email="staff@test.com",
            password="test123",
            role="staff",
        )

        # Create profiles, aircraft, mission, and flight plan...
        # (Similar setup as FlightPlanModelTest)
        self.client_profile = ClientProfile.objects.create(
            user=self.client_user,
            company_name="Test Company",
            contact_person="John Client",
            phone_number="+61412345678",
            address="123 Test St",
        )

        self.pilot_profile = PilotProfile.objects.create(
            user=self.pilot_user,
            license_number="RPL001",
            license_type="reoc",
            medical_certificate_expiry=timezone.now().date() + timedelta(days=365),
            flight_review_expiry=timezone.now().date() + timedelta(days=180),
            total_flight_hours=Decimal("150.5"),
        )

        self.staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            position="Mission Commander",
            employee_id="EMP001",
            phone_number="+61412345679",
            emergency_contact="Jane Emergency",
            emergency_phone="+61412345680",
        )

        self.aircraft_type = AircraftType.objects.create(
            name="Test Aircraft",
            manufacturer="Test Mfg",
            model="Test Model",
            category="small",
            operation_type="commercial",
            maximum_takeoff_weight=Decimal("15.0"),
            maximum_operating_height=400,
        )

        self.aircraft = Aircraft.objects.create(
            registration_mark="LOG-001",
            aircraft_type=self.aircraft_type,
            owner=self.client_profile,
            serial_number="SN789012",
            year_manufactured=2023,
        )

        self.mission = Mission.objects.create(
            name="Log Test Mission",
            mission_type="commercial",
            description="Test",
            client=self.client_profile,
            mission_commander=self.staff_profile,
            planned_start_date=timezone.now() + timedelta(days=1),
            planned_end_date=timezone.now() + timedelta(days=2),
        )

        self.flight_plan = FlightPlan.objects.create(
            mission=self.mission,
            aircraft=self.aircraft,
            pilot_in_command=self.pilot_profile,
            flight_type="line_of_sight",
            departure_location="Test Airfield",
            departure_latitude=Decimal("-33.946910"),
            departure_longitude=Decimal("151.177002"),
            planned_altitude_agl=120,
            maximum_range_from_pilot=500,
            planned_departure_time=timezone.now() + timedelta(hours=2),
            estimated_flight_time=timedelta(minutes=30),
            weather_minimums="VMC",
            planned_weather_check_time=timezone.now() + timedelta(hours=1),
            emergency_procedures="Emergency",
            lost_link_procedures="Lost link",
        )

    def test_flight_log_creation(self):
        """Test basic flight log creation"""
        takeoff_time = timezone.now()
        landing_time = takeoff_time + timedelta(minutes=25)

        flight_log = FlightLog.objects.create(
            flight_plan=self.flight_plan,
            takeoff_time=takeoff_time,
            landing_time=landing_time,
            flight_time=landing_time - takeoff_time,
            maximum_altitude_achieved=115,
            maximum_range_achieved=450,
            pre_flight_battery_voltage=Decimal("12.6"),
            post_flight_battery_voltage=Decimal("11.8"),
            wind_speed_takeoff=8,
            wind_direction_takeoff=270,
            temperature_celsius=22,
            visibility_meters=10000,
            objectives_achieved=True,
        )

        self.assertEqual(flight_log.flight_plan, self.flight_plan)
        self.assertTrue(flight_log.log_id.startswith("LOG-"))
        self.assertTrue(flight_log.objectives_achieved)

    def test_flight_log_time_validation(self):
        """Test flight log time validation"""
        takeoff_time = timezone.now()
        landing_time = takeoff_time - timedelta(minutes=10)  # Invalid: before takeoff

        flight_log = FlightLog(
            flight_plan=self.flight_plan,
            takeoff_time=takeoff_time,
            landing_time=landing_time,
            flight_time=timedelta(minutes=25),
            maximum_altitude_achieved=115,
            maximum_range_achieved=450,
            pre_flight_battery_voltage=Decimal("12.6"),
            post_flight_battery_voltage=Decimal("11.8"),
            wind_speed_takeoff=8,
            wind_direction_takeoff=270,
            temperature_celsius=22,
            visibility_meters=10000,
        )

        with self.assertRaises(ValidationError):
            flight_log.clean()

    def test_flight_log_properties(self):
        """Test flight log property methods"""
        takeoff_time = timezone.now()
        landing_time = takeoff_time + timedelta(minutes=30)

        flight_log = FlightLog.objects.create(
            flight_plan=self.flight_plan,
            takeoff_time=takeoff_time,
            landing_time=landing_time,
            flight_time=landing_time - takeoff_time,
            maximum_altitude_achieved=115,
            maximum_range_achieved=1000,  # 1km
            pre_flight_battery_voltage=Decimal("12.6"),
            post_flight_battery_voltage=Decimal("11.8"),
            wind_speed_takeoff=8,
            wind_direction_takeoff=270,
            temperature_celsius=22,
            visibility_meters=10000,
        )

        self.assertEqual(flight_log.total_flight_hours, 0.5)  # 30 minutes = 0.5 hours
        self.assertIsNotNone(flight_log.average_ground_speed)
