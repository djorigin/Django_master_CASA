"""
Aircraft signals for automatic data integrity maintenance
Philosophy: Minimize human intervention, maximize accuracy
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


@receiver([post_save, post_delete], sender='flight_operations.FlightLog')
def update_aircraft_flight_hours(sender, instance, **kwargs):
    """
    Auto-update aircraft flight hours when flight logs change

    Data Integrity Philosophy:
    - Single source of truth: Flight logs drive aircraft hours
    - No manual intervention needed
    - Backdating logs automatically recalculates totals
    - Compliance tracking stays accurate
    """
    if instance.aircraft:
        instance.aircraft.update_flight_hours()
