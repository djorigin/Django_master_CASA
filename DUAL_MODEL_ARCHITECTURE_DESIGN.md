# Dual-Model Flight Planning Architecture Design

## Overview
Implementing separate AircraftFlightPlan and DroneFlightPlan models while maintaining database normalization and minimizing code duplication through smart business logic.

## Architecture Components

### 1. Abstract Base Model (Normalization Solution)
```python
class BaseFlightPlan(models.Model):
    """
    Abstract base class containing common flight planning fields
    Addresses normalization by centralizing shared logic
    """
    class Meta:
        abstract = True
    
    # Core fields present in both aircraft and drone operations
    mission = models.ForeignKey('Mission', on_delete=models.CASCADE)
    flight_plan_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Common timing fields
    planned_departure_time = models.DateTimeField()
    planned_arrival_time = models.DateTimeField()
    estimated_flight_time = models.DurationField()
    
    # Shared operational fields
    weather_conditions = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)
    emergency_procedures = models.TextField(blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def clean(self):
        """Shared validation logic"""
        if self.planned_arrival_time <= self.planned_departure_time:
            raise ValidationError("Arrival time must be after departure time")
    
    def get_flight_duration_hours(self):
        """Business logic method available to both models"""
        return self.estimated_flight_time.total_seconds() / 3600
    
    @abstractmethod
    def get_operational_requirements(self):
        """Force implementation in concrete classes"""
        pass
```

### 2. Aircraft Flight Plan Model
```python
class AircraftFlightPlan(BaseFlightPlan):
    """Traditional aircraft flight planning with aviation-specific requirements"""
    
    # Aircraft-specific relationships
    aircraft = models.ForeignKey('aircraft.Aircraft', on_delete=models.CASCADE)
    pilot_in_command = models.ForeignKey('accounts.PilotProfile', on_delete=models.CASCADE)
    co_pilot = models.ForeignKey('accounts.PilotProfile', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Aviation navigation fields
    departure_airport = models.CharField(max_length=4)  # ICAO code
    arrival_airport = models.CharField(max_length=4)    # ICAO code
    alternate_airport = models.CharField(max_length=4, blank=True)
    route = models.TextField()  # Airways and waypoints
    cruise_altitude = models.IntegerField()  # Feet MSL
    
    # Aircraft performance fields
    fuel_required = models.DecimalField(max_digits=8, decimal_places=2)  # Liters
    fuel_loaded = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    payload_weight = models.DecimalField(max_digits=8, decimal_places=2)  # Kg
    
    # Regulatory compliance
    flight_rules = models.CharField(max_length=3, choices=[('VFR', 'VFR'), ('IFR', 'IFR')])
    atc_clearance = models.TextField(blank=True)
    
    def get_operational_requirements(self):
        return {
            'fuel_endurance_hours': self.fuel_required / self.aircraft.fuel_consumption_per_hour,
            'weight_and_balance_check': self.payload_weight <= self.aircraft.max_payload,
            'crew_qualifications': self.validate_crew_certifications(),
        }
    
    def validate_crew_certifications(self):
        """Aircraft-specific crew validation"""
        required_certs = ['PPL', 'Medical Certificate', 'Aircraft Type Rating']
        return all(self.pilot_in_command.has_valid_certificate(cert) for cert in required_certs)
```

### 3. Drone Flight Plan Model
```python
class DroneFlightPlan(BaseFlightPlan):
    """RPAS/Drone flight planning with UAS-specific requirements"""
    
    # Drone-specific relationships
    drone = models.ForeignKey('aircraft.Drone', on_delete=models.CASCADE)  # New model needed
    remote_pilot = models.ForeignKey('accounts.PilotProfile', on_delete=models.CASCADE)
    visual_observer = models.ForeignKey('accounts.StaffProfile', on_delete=models.SET_NULL, null=True, blank=True)
    
    # RPAS navigation fields
    takeoff_location = models.CharField(max_length=100)
    landing_location = models.CharField(max_length=100)
    operating_area_coordinates = models.JSONField()  # Polygon boundary
    maximum_altitude_agl = models.IntegerField()  # Feet AGL
    
    # Drone performance fields
    battery_capacity = models.DecimalField(max_digits=6, decimal_places=2)  # mAh
    estimated_battery_consumption = models.DecimalField(max_digits=5, decimal_places=2)  # %
    payload_description = models.TextField()
    
    # RPAS regulatory compliance
    casa_approval_number = models.CharField(max_length=50, blank=True)  # ReOC/RPA Operator Certificate
    airspace_approval = models.CharField(max_length=100, blank=True)
    no_fly_zones_checked = models.BooleanField(default=False)
    
    # Automated flight features
    waypoints = models.JSONField(default=list)  # GPS coordinates array
    autonomous_mode = models.BooleanField(default=False)
    return_to_home_altitude = models.IntegerField(default=100)  # Feet AGL
    
    def get_operational_requirements(self):
        return {
            'battery_endurance_minutes': self.calculate_battery_life(),
            'airspace_compliance': self.validate_airspace_restrictions(),
            'remote_pilot_qualifications': self.validate_rpas_certifications(),
        }
    
    def calculate_battery_life(self):
        """Drone-specific battery calculation"""
        base_flight_time = (self.battery_capacity * 0.8) / self.drone.power_consumption_per_minute
        return base_flight_time * (1 - self.estimated_battery_consumption/100)
    
    def validate_rpas_certifications(self):
        """RPAS-specific pilot validation"""
        required_certs = ['ReOC', 'Remote Pilot Licence', 'Aviation Medical Certificate']
        return all(self.remote_pilot.has_valid_certificate(cert) for cert in required_certs)
```

## Smart Business Logic Solutions

### 1. Unified Flight Plan Manager
```python
class FlightPlanManager:
    """
    Business logic layer that handles both aircraft and drone operations
    Prevents code duplication while maintaining type safety
    """
    
    @staticmethod
    def create_flight_plan(mission, operation_type, **kwargs):
        """Factory method for creating appropriate flight plan type"""
        if operation_type == 'aircraft':
            return AircraftFlightPlan.objects.create(mission=mission, **kwargs)
        elif operation_type == 'drone':
            return DroneFlightPlan.objects.create(mission=mission, **kwargs)
        else:
            raise ValueError(f"Unsupported operation type: {operation_type}")
    
    @staticmethod
    def get_all_flight_plans(mission):
        """Return unified view of all flight plans for a mission"""
        aircraft_plans = AircraftFlightPlan.objects.filter(mission=mission)
        drone_plans = DroneFlightPlan.objects.filter(mission=mission)
        
        # Return as unified queryset with type indicators
        return {
            'aircraft_plans': aircraft_plans,
            'drone_plans': drone_plans,
            'total_count': aircraft_plans.count() + drone_plans.count()
        }
    
    @staticmethod
    def validate_mission_flight_plans(mission):
        """Cross-type validation for mission feasibility"""
        all_plans = FlightPlanManager.get_all_flight_plans(mission)
        
        # Check for airspace conflicts between aircraft and drone operations
        conflicts = []
        for aircraft_plan in all_plans['aircraft_plans']:
            for drone_plan in all_plans['drone_plans']:
                if FlightPlanManager._check_airspace_conflict(aircraft_plan, drone_plan):
                    conflicts.append((aircraft_plan, drone_plan))
        
        return {
            'is_valid': len(conflicts) == 0,
            'conflicts': conflicts
        }
```

### 2. Generic Template Support
```python
# In views.py
class MissionDetailView(DetailView):
    model = Mission
    template_name = 'flight_operations/mission_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Use FlightPlanManager for unified data
        flight_plans = FlightPlanManager.get_all_flight_plans(self.object)
        context.update(flight_plans)
        
        return context
```

### 3. Database Normalization Preservation
- **No data duplication**: Common fields only exist in BaseFlightPlan
- **Proper relationships**: Foreign keys maintain referential integrity
- **Shared business logic**: Methods inherited from base class
- **Type-specific extensions**: Only operation-specific fields in concrete models

## Migration Strategy

### Phase 1: Create Base Infrastructure
1. Create BaseFlightPlan abstract model
2. Add Drone model to aircraft app
3. Update Mission model relationships

### Phase 2: Implement Concrete Models
1. Create AircraftFlightPlan model
2. Create DroneFlightPlan model
3. Migrate existing FlightPlan data to AircraftFlightPlan

### Phase 3: Update Business Logic
1. Implement FlightPlanManager
2. Update views to use manager
3. Update templates for dual model support

### Phase 4: Forms and Validation
1. Create operation-type-specific forms
2. Add client-side operation type selection
3. Implement cross-type validation

## Benefits of This Approach

✅ **Maintains current structure**: Existing code continues to work
✅ **Database normalization**: No field duplication, proper inheritance
✅ **Type safety**: Each operation type has appropriate fields
✅ **Extensibility**: Easy to add new operation types (helicopters, gliders)
✅ **Business logic reuse**: Shared methods prevent code duplication
✅ **Testing compatibility**: Your systematic testing approach will catch all integration issues

## File Structure Impact
```
flight_operations/
├── models.py (add BaseFlightPlan, AircraftFlightPlan, DroneFlightPlan)
├── managers.py (new file for FlightPlanManager)
├── forms.py (add operation-type-specific forms)
├── views.py (update to use FlightPlanManager)
└── templates/
    ├── flight_plans/
    │   ├── aircraft_flight_plan_form.html
    │   ├── drone_flight_plan_form.html
    │   └── operation_type_selector.html
    └── mission_detail.html (update for dual model display)

aircraft/
├── models.py (add Drone model)
```

This design addresses all your concerns while leveraging Django's strengths for maintainable, scalable code.