from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import AircraftForm, AircraftTypeForm
from .models import Aircraft, AircraftType


@login_required
def aircraft_dashboard(request):
    """Main aircraft dashboard with statistics"""
    total_aircraft = Aircraft.objects.count()
    active_aircraft = Aircraft.objects.filter(status="operational").count()
    aircraft_types = AircraftType.objects.filter(is_active=True).count()
    
    # Aircraft status breakdown
    status_breakdown = {}
    for status_choice in Aircraft.STATUS_CHOICES:
        status_code = status_choice[0]
        status_breakdown[status_choice[1]] = Aircraft.objects.filter(
            status=status_code
        ).count()

    # Recent aircraft additions
    recent_aircraft = Aircraft.objects.order_by("-acquisition_date")[:5]
    
    # Aircraft requiring inspection soon (within 30 days)
    upcoming_inspections = Aircraft.objects.filter(
        next_inspection_due__lte=timezone.now().date() + timezone.timedelta(days=30),
        status="operational"
    ).count()

    context = {
        "total_aircraft": total_aircraft,
        "active_aircraft": active_aircraft,
        "aircraft_types": aircraft_types,
        "status_breakdown": status_breakdown,
        "recent_aircraft": recent_aircraft,
        "upcoming_inspections": upcoming_inspections,
    }
    return render(request, "aircraft/dashboard.html", context)


# AircraftType Views
@login_required
def aircraft_type_list(request):
    """List all aircraft types with search and filtering"""
    aircraft_types = AircraftType.objects.all().order_by("manufacturer", "model")

    # Search functionality
    search_query = request.GET.get("search")
    if search_query:
        aircraft_types = aircraft_types.filter(
            Q(name__icontains=search_query)
            | Q(manufacturer__icontains=search_query)
            | Q(model__icontains=search_query)
        )

    # Category filtering
    category_filter = request.GET.get("category")
    if category_filter:
        aircraft_types = aircraft_types.filter(category=category_filter)

    # Operation type filtering
    operation_filter = request.GET.get("operation_type")
    if operation_filter:
        aircraft_types = aircraft_types.filter(operation_type=operation_filter)

    # Active status filtering
    active_filter = request.GET.get("active")
    if active_filter:
        aircraft_types = aircraft_types.filter(is_active=active_filter == "true")

    paginator = Paginator(aircraft_types, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "category_filter": category_filter,
        "operation_filter": operation_filter,
        "active_filter": active_filter,
        "category_choices": AircraftType.CATEGORY_CHOICES,
        "operation_choices": AircraftType.OPERATION_TYPE_CHOICES,
    }
    return render(request, "aircraft/aircraft_type_list.html", context)


@login_required
def aircraft_type_detail(request, pk):
    """Display detailed aircraft type information"""
    aircraft_type = get_object_or_404(AircraftType, pk=pk)
    aircraft_count = Aircraft.objects.filter(aircraft_type=aircraft_type).count()
    recent_aircraft = Aircraft.objects.filter(aircraft_type=aircraft_type).order_by(
        "-acquisition_date"
    )[:5]

    context = {
        "aircraft_type": aircraft_type,
        "aircraft_count": aircraft_count,
        "recent_aircraft": recent_aircraft,
    }
    return render(request, "aircraft/aircraft_type_detail.html", context)


@login_required
def aircraft_type_create(request):
    """Create new aircraft type"""
    if request.method == "POST":
        form = AircraftTypeForm(request.POST)
        if form.is_valid():
            aircraft_type = form.save()
            messages.success(
                request, f"Aircraft type {aircraft_type.name} created successfully."
            )
            return redirect("aircraft:aircraft_type_detail", pk=aircraft_type.pk)
    else:
        form = AircraftTypeForm()

    context = {"form": form, "action": "Create"}
    return render(request, "aircraft/aircraft_type_form.html", context)


@login_required
def aircraft_type_update(request, pk):
    """Update existing aircraft type"""
    aircraft_type = get_object_or_404(AircraftType, pk=pk)
    
    if request.method == "POST":
        form = AircraftTypeForm(request.POST, instance=aircraft_type)
        if form.is_valid():
            aircraft_type = form.save()
            messages.success(
                request, f"Aircraft type {aircraft_type.name} updated successfully."
            )
            return redirect("aircraft:aircraft_type_detail", pk=aircraft_type.pk)
    else:
        form = AircraftTypeForm(instance=aircraft_type)

    context = {"form": form, "action": "Update", "aircraft_type": aircraft_type}
    return render(request, "aircraft/aircraft_type_form.html", context)


@login_required
@require_http_methods(["DELETE"])
def aircraft_type_delete(request, pk):
    """Delete aircraft type (AJAX only)"""
    aircraft_type = get_object_or_404(AircraftType, pk=pk)
    
    # Check if any aircraft use this type
    aircraft_count = Aircraft.objects.filter(aircraft_type=aircraft_type).count()
    if aircraft_count > 0:
        return JsonResponse({
            "success": False,
            "message": f"Cannot delete aircraft type. {aircraft_count} aircraft are using this type."
        })
    
    aircraft_type_name = aircraft_type.name
    aircraft_type.delete()
    
    return JsonResponse({
        "success": True,
        "message": f"Aircraft type {aircraft_type_name} deleted successfully."
    })


# Aircraft Views
@login_required
def aircraft_list(request):
    """List all aircraft with search and filtering"""
    aircraft = Aircraft.objects.select_related("aircraft_type").order_by("-acquisition_date")

    # Search functionality
    search_query = request.GET.get("search")
    if search_query:
        aircraft = aircraft.filter(
            Q(aircraft_id__icontains=search_query)
            | Q(registration_number__icontains=search_query)
            | Q(serial_number__icontains=search_query)
            | Q(aircraft_type__name__icontains=search_query)
        )

    # Status filtering
    status_filter = request.GET.get("status")
    if status_filter:
        aircraft = aircraft.filter(status=status_filter)

    # Aircraft type filtering
    type_filter = request.GET.get("aircraft_type")
    if type_filter:
        aircraft = aircraft.filter(aircraft_type_id=type_filter)

    # Active status filtering
    active_filter = request.GET.get("active")
    if active_filter:
        aircraft = aircraft.filter(is_active=active_filter == "true")

    paginator = Paginator(aircraft, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "status_filter": status_filter,
        "type_filter": type_filter,
        "active_filter": active_filter,
        "status_choices": Aircraft.STATUS_CHOICES,
        "aircraft_types": AircraftType.objects.filter(is_active=True),
    }
    return render(request, "aircraft/aircraft_list.html", context)


@login_required
def aircraft_detail(request, pk):
    """Display detailed aircraft information"""
    aircraft = get_object_or_404(Aircraft.objects.select_related("aircraft_type"), pk=pk)
    
    # Calculate days until next inspection
    days_to_inspection = None
    if aircraft.next_inspection_due:
        days_to_inspection = (aircraft.next_inspection_due - timezone.now().date()).days

    context = {
        "aircraft": aircraft,
        "days_to_inspection": days_to_inspection,
    }
    return render(request, "aircraft/aircraft_detail.html", context)


@login_required
def aircraft_create(request):
    """Create new aircraft"""
    if request.method == "POST":
        form = AircraftForm(request.POST)
        if form.is_valid():
            aircraft = form.save()
            messages.success(
                request, f"Aircraft {aircraft.aircraft_id} created successfully."
            )
            return redirect("aircraft:aircraft_detail", pk=aircraft.pk)
    else:
        form = AircraftForm()

    context = {"form": form, "action": "Create"}
    return render(request, "aircraft/aircraft_form.html", context)


@login_required
def aircraft_update(request, pk):
    """Update existing aircraft"""
    aircraft = get_object_or_404(Aircraft, pk=pk)
    
    if request.method == "POST":
        form = AircraftForm(request.POST, instance=aircraft)
        if form.is_valid():
            aircraft = form.save()
            messages.success(
                request, f"Aircraft {aircraft.aircraft_id} updated successfully."
            )
            return redirect("aircraft:aircraft_detail", pk=aircraft.pk)
    else:
        form = AircraftForm(instance=aircraft)

    context = {"form": form, "action": "Update", "aircraft": aircraft}
    return render(request, "aircraft/aircraft_form.html", context)


@login_required
@require_http_methods(["DELETE"])
def aircraft_delete(request, pk):
    """Delete aircraft (AJAX only)"""
    aircraft = get_object_or_404(Aircraft, pk=pk)
    
    aircraft_id = aircraft.aircraft_id
    aircraft.delete()
    
    return JsonResponse({
        "success": True,
        "message": f"Aircraft {aircraft_id} deleted successfully."
    })