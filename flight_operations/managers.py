"""
Flight Plan Manager - Business Logic Layer
Handles unified operations between AircraftFlightPlan and DroneFlightPlan models.
Prevents code duplication while maintaining type safety.
"""

from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import AircraftFlightPlan, DroneFlightPlan


class FlightPlanManager:
    """
    Business logic layer that handles both aircraft and drone operations.
    Provides unified interface while maintaining operation-specific functionality.
    """

    @staticmethod
    def create_flight_plan(mission, operation_type, **kwargs):
        """
        Factory method for creating appropriate flight plan type.

        Args:
            mission: Mission instance
            operation_type: 'aircraft' or 'drone'
            **kwargs: Fields specific to the flight plan type

        Returns:
            AircraftFlightPlan or DroneFlightPlan instance
        """
        if operation_type == 'aircraft':
            return AircraftFlightPlan.objects.create(mission=mission, **kwargs)
        elif operation_type == 'drone':
            return DroneFlightPlan.objects.create(mission=mission, **kwargs)
        else:
            raise ValueError(
                f"Unsupported operation type: {operation_type}. Use 'aircraft' or 'drone'."
            )

    @staticmethod
    def get_all_flight_plans(mission):
        """
        Return unified view of all flight plans for a mission.

        Args:
            mission: Mission instance

        Returns:
            Dict with aircraft_plans, drone_plans, and total_count
        """
        aircraft_plans = AircraftFlightPlan.objects.filter(
            mission=mission
        ).select_related('aircraft', 'pilot_in_command__user', 'co_pilot__user')
        drone_plans = DroneFlightPlan.objects.filter(mission=mission).select_related(
            'drone', 'remote_pilot__user', 'visual_observer__user'
        )

        return {
            'aircraft_plans': aircraft_plans,
            'drone_plans': drone_plans,
            'total_count': aircraft_plans.count() + drone_plans.count(),
            'all_plans': list(aircraft_plans)
            + list(drone_plans),  # Combined list for templates
        }

    @staticmethod
    def get_flight_plan_by_id(flight_plan_id):
        """
        Get flight plan by ID regardless of type.

        Args:
            flight_plan_id: Flight plan identifier

        Returns:
            AircraftFlightPlan or DroneFlightPlan instance, or None
        """
        try:
            return AircraftFlightPlan.objects.get(flight_plan_id=flight_plan_id)
        except AircraftFlightPlan.DoesNotExist:
            try:
                return DroneFlightPlan.objects.get(flight_plan_id=flight_plan_id)
            except DroneFlightPlan.DoesNotExist:
                return None

    @staticmethod
    def validate_mission_flight_plans(mission):
        """
        Cross-type validation for mission feasibility.

        Args:
            mission: Mission instance

        Returns:
            Dict with validation results and any conflicts
        """
        all_plans = FlightPlanManager.get_all_flight_plans(mission)
        conflicts = []
        warnings = []

        # Check for timing conflicts between plans
        for plan1 in all_plans['all_plans']:
            for plan2 in all_plans['all_plans']:
                if plan1.id != plan2.id:
                    conflict = FlightPlanManager._check_timing_conflict(plan1, plan2)
                    if conflict:
                        conflicts.append(conflict)

        # Check for airspace conflicts between aircraft and drone operations
        for aircraft_plan in all_plans['aircraft_plans']:
            for drone_plan in all_plans['drone_plans']:
                airspace_conflict = FlightPlanManager._check_airspace_conflict(
                    aircraft_plan, drone_plan
                )
                if airspace_conflict:
                    conflicts.append(airspace_conflict)

        # Check for resource conflicts (same pilot, same aircraft)
        resource_conflicts = FlightPlanManager._check_resource_conflicts(
            all_plans['all_plans']
        )
        conflicts.extend(resource_conflicts)

        return {
            'is_valid': len(conflicts) == 0,
            'conflicts': conflicts,
            'warnings': warnings,
            'total_plans': all_plans['total_count'],
        }

    @staticmethod
    def _check_timing_conflict(plan1, plan2):
        """Check for timing conflicts between two flight plans"""
        if not (
            plan1.planned_departure_time
            and plan1.planned_arrival_time
            and plan2.planned_departure_time
            and plan2.planned_arrival_time
        ):
            return None

        # Check for overlapping time periods
        if (
            plan1.planned_departure_time < plan2.planned_arrival_time
            and plan1.planned_arrival_time > plan2.planned_departure_time
        ):
            return {
                'type': 'timing_overlap',
                'plan1': plan1.flight_plan_id,
                'plan2': plan2.flight_plan_id,
                'message': f"Flight plans {plan1.flight_plan_id} and {plan2.flight_plan_id} have overlapping times",
            }
        return None

    @staticmethod
    def _check_airspace_conflict(aircraft_plan, drone_plan):
        """Check for airspace conflicts between aircraft and drone operations"""
        # Simplified airspace conflict detection
        # In a real system, this would use detailed airspace geometry

        if not (
            aircraft_plan.planned_departure_time
            and aircraft_plan.planned_arrival_time
            and drone_plan.planned_departure_time
            and drone_plan.planned_arrival_time
        ):
            return None

        # Check for temporal overlap
        time_overlap = (
            aircraft_plan.planned_departure_time < drone_plan.planned_arrival_time
            and aircraft_plan.planned_arrival_time > drone_plan.planned_departure_time
        )

        if time_overlap:
            # Check altitude separation
            aircraft_alt = getattr(aircraft_plan, 'cruise_altitude', 0)
            drone_alt = getattr(drone_plan, 'maximum_altitude_agl', 0)

            # Convert drone AGL to approximate MSL (simplified)
            drone_alt_msl = drone_alt + 1000  # Assume 1000ft ground elevation

            # Check for altitude conflict (within 1000ft separation)
            if abs(aircraft_alt - drone_alt_msl) < 1000:
                return {
                    'type': 'airspace_conflict',
                    'aircraft_plan': aircraft_plan.flight_plan_id,
                    'drone_plan': drone_plan.flight_plan_id,
                    'message': f"Potential airspace conflict between {aircraft_plan.flight_plan_id} and {drone_plan.flight_plan_id}",
                }

        return None

    @staticmethod
    def _check_resource_conflicts(all_plans):
        """Check for resource conflicts (pilot, aircraft) between flight plans"""
        conflicts = []

        for i, plan1 in enumerate(all_plans):
            for plan2 in all_plans[i + 1 :]:
                # Check pilot conflicts
                pilot_conflict = FlightPlanManager._check_pilot_conflict(plan1, plan2)
                if pilot_conflict:
                    conflicts.append(pilot_conflict)

                # Check aircraft conflicts
                aircraft_conflict = FlightPlanManager._check_aircraft_conflict(
                    plan1, plan2
                )
                if aircraft_conflict:
                    conflicts.append(aircraft_conflict)

        return conflicts

    @staticmethod
    def _check_pilot_conflict(plan1, plan2):
        """Check if the same pilot is assigned to overlapping flights"""
        # Get pilots from both plans
        plan1_pilots = set()
        plan2_pilots = set()

        # Extract pilots based on plan type
        if hasattr(plan1, 'pilot_in_command'):
            plan1_pilots.add(plan1.pilot_in_command.id)
        if hasattr(plan1, 'remote_pilot'):
            plan1_pilots.add(plan1.remote_pilot.id)
        if hasattr(plan1, 'co_pilot') and plan1.co_pilot:
            plan1_pilots.add(plan1.co_pilot.id)

        if hasattr(plan2, 'pilot_in_command'):
            plan2_pilots.add(plan2.pilot_in_command.id)
        if hasattr(plan2, 'remote_pilot'):
            plan2_pilots.add(plan2.remote_pilot.id)
        if hasattr(plan2, 'co_pilot') and plan2.co_pilot:
            plan2_pilots.add(plan2.co_pilot.id)

        # Check for common pilots and time overlap
        common_pilots = plan1_pilots.intersection(plan2_pilots)
        if common_pilots and FlightPlanManager._check_timing_conflict(plan1, plan2):
            return {
                'type': 'pilot_conflict',
                'plan1': plan1.flight_plan_id,
                'plan2': plan2.flight_plan_id,
                'message': f"Pilot conflict between {plan1.flight_plan_id} and {plan2.flight_plan_id}",
            }

        return None

    @staticmethod
    def _check_aircraft_conflict(plan1, plan2):
        """Check if the same aircraft is assigned to overlapping flights"""
        # Get aircraft from both plans
        aircraft1 = getattr(plan1, 'aircraft', None) or getattr(plan1, 'drone', None)
        aircraft2 = getattr(plan2, 'aircraft', None) or getattr(plan2, 'drone', None)

        if (
            aircraft1
            and aircraft2
            and aircraft1.id == aircraft2.id
            and FlightPlanManager._check_timing_conflict(plan1, plan2)
        ):
            return {
                'type': 'aircraft_conflict',
                'plan1': plan1.flight_plan_id,
                'plan2': plan2.flight_plan_id,
                'message': f"Aircraft conflict between {plan1.flight_plan_id} and {plan2.flight_plan_id}",
            }

        return None

    @staticmethod
    def get_flight_statistics(mission=None):
        """
        Get flight plan statistics.

        Args:
            mission: Optional mission to filter by

        Returns:
            Dict with statistics for aircraft and drone operations
        """
        aircraft_qs = AircraftFlightPlan.objects.all()
        drone_qs = DroneFlightPlan.objects.all()

        if mission:
            aircraft_qs = aircraft_qs.filter(mission=mission)
            drone_qs = drone_qs.filter(mission=mission)

        return {
            'aircraft': {
                'total': aircraft_qs.count(),
                'draft': aircraft_qs.filter(status='draft').count(),
                'approved': aircraft_qs.filter(status='approved').count(),
                'active': aircraft_qs.filter(status='active').count(),
                'completed': aircraft_qs.filter(status='completed').count(),
            },
            'drone': {
                'total': drone_qs.count(),
                'draft': drone_qs.filter(status='draft').count(),
                'approved': drone_qs.filter(status='approved').count(),
                'active': drone_qs.filter(status='active').count(),
                'completed': drone_qs.filter(status='completed').count(),
            },
        }
