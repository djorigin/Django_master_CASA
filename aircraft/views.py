from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import Aircraft, AircraftType


class AircraftListView(LoginRequiredMixin, ListView):
    """
    List view for aircraft with CASA compliance status
    """

    model = Aircraft
    template_name = "aircraft/aircraft_list.html"
    context_object_name = "aircraft_list"
    paginate_by = 20

    def get_queryset(self):
        return Aircraft.objects.select_related(
            "aircraft_type", "owner", "operator"
        ).order_by("registration_mark")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add summary statistics
        queryset = self.get_queryset()
        context["total_aircraft"] = queryset.count()
        context["operational_aircraft"] = sum(
            1 for aircraft in queryset if aircraft.is_operational
        )
        context["pending_maintenance"] = sum(
            1
            for aircraft in queryset
            if aircraft.maintenance_status in ["due_soon", "overdue"]
        )

        return context


class AircraftDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for individual aircraft
    """

    model = Aircraft
    template_name = "aircraft/aircraft_detail.html"
    context_object_name = "aircraft"
    slug_field = "registration_mark"
    slug_url_kwarg = "registration_mark"


@login_required
def aircraft_status_api(request, registration_mark):
    """
    API endpoint for aircraft status information
    """
    try:
        aircraft = Aircraft.objects.select_related("aircraft_type").get(
            registration_mark=registration_mark
        )

        return JsonResponse(
            {
                "registration_mark": aircraft.registration_mark,
                "status": aircraft.status,
                "is_operational": aircraft.is_operational,
                "is_airworthy": aircraft.is_airworthy,
                "is_insured": aircraft.is_insured,
                "maintenance_status": aircraft.maintenance_status,
                "aircraft_type": {
                    "manufacturer": aircraft.aircraft_type.manufacturer,
                    "model": aircraft.aircraft_type.model,
                    "category": aircraft.aircraft_type.category,
                },
            }
        )
    except Aircraft.DoesNotExist:
        return JsonResponse({"error": "Aircraft not found"}, status=404)


@login_required
def aircraft_compliance_dashboard(request):
    """
    Dashboard view showing CASA compliance overview
    """
    aircraft_qs = Aircraft.objects.select_related("aircraft_type", "owner")

    # Compliance statistics
    stats = {
        "total_aircraft": aircraft_qs.count(),
        "operational": sum(1 for a in aircraft_qs if a.is_operational),
        "maintenance_due": sum(
            1 for a in aircraft_qs if a.maintenance_status == "due_soon"
        ),
        "maintenance_overdue": sum(
            1 for a in aircraft_qs if a.maintenance_status == "overdue"
        ),
        "airworthiness_expiring": sum(
            1
            for a in aircraft_qs
            if a.airworthiness_valid_until
            and (a.airworthiness_valid_until - timezone.now().date()).days <= 30
        ),
    }

    # Aircraft by category
    categories = {}
    for aircraft in aircraft_qs:
        cat = aircraft.aircraft_type.get_category_display()
        categories[cat] = categories.get(cat, 0) + 1

    context = {
        "stats": stats,
        "categories": categories,
        "recent_aircraft": aircraft_qs.order_by("-registration_date")[:5],
    }

    return render(request, "aircraft/compliance_dashboard.html", context)
