from django.apps import AppConfig


class AircraftConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aircraft"

    def ready(self):
        """
        Initialize signals for automatic data integrity
        Philosophy: Let the system maintain accuracy, not humans
        """
        import aircraft.signals
