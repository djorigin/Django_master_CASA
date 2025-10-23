from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import AirspaceClassForm, OperationalAreaForm
from .models import AirspaceClass, OperationalArea


@login_required
def airspace_dashboard(request):
    """Main airspace dashboard with statistics"""
    total_airspace_classes = AirspaceClass.objects.count()
    total_operational_areas = OperationalArea.objects.count()
    active_operational_areas = OperationalArea.objects.filter(status="active").count()

    # Airspace class breakdown
    class_breakdown = {}
    for airspace_class in AirspaceClass.objects.all():
        class_breakdown[airspace_class.name] = OperationalArea.objects.filter(
            airspace_class=airspace_class
        ).count()

    # Area type breakdown
    area_type_breakdown = {}
    for area_type_choice in OperationalArea.AREA_TYPE_CHOICES:
        area_type_code = area_type_choice[0]
        area_type_breakdown[area_type_choice[1]] = OperationalArea.objects.filter(
            area_type=area_type_code
        ).count()

    # Recent operational areas
    recent_areas = OperationalArea.objects.order_by("-created_at")[:5]

    # Areas requiring authorization
    auth_required_areas = OperationalArea.objects.filter(
        authorization_required=True, status="active"
    ).count()

    # Temporary areas (active and expiring within 7 days)
    upcoming_expiries = OperationalArea.objects.filter(
        status="temporary",
        effective_until__lte=timezone.now() + timezone.timedelta(days=7),
        effective_until__gt=timezone.now(),
    ).count()

    context = {
        "total_airspace_classes": total_airspace_classes,
        "total_operational_areas": total_operational_areas,
        "active_operational_areas": active_operational_areas,
        "class_breakdown": class_breakdown,
        "area_type_breakdown": area_type_breakdown,
        "recent_areas": recent_areas,
        "auth_required_areas": auth_required_areas,
        "upcoming_expiries": upcoming_expiries,
    }
    return render(request, "airspace/dashboard.html", context)


# AirspaceClass Views
@login_required
def airspace_class_list(request):
    """List all airspace classes with search and filtering"""
    airspace_classes = AirspaceClass.objects.all()

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        airspace_classes = airspace_classes.filter(
            Q(airspace_class__icontains=search_query)
            | Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    # Filter by authorization level
    auth_level = request.GET.get("authorization_level", "")
    if auth_level:
        airspace_classes = airspace_classes.filter(authorization_level=auth_level)

    # Filter by pilot license required
    pilot_license = request.GET.get("pilot_license", "")
    if pilot_license:
        airspace_classes = airspace_classes.filter(pilot_license_required=pilot_license)

    # Pagination
    paginator = Paginator(airspace_classes, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get filter choices for template
    authorization_choices = AirspaceClass.AUTHORIZATION_LEVEL_CHOICES
    pilot_license_choices = [
        ("none", "None Required"),
        ("reoc", "ReOC Required"),
        ("rpl", "Remote Pilot License"),
        ("cpl", "Commercial Pilot License"),
    ]

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "auth_level": auth_level,
        "pilot_license": pilot_license,
        "authorization_choices": authorization_choices,
        "pilot_license_choices": pilot_license_choices,
    }
    return render(request, "airspace/airspace_class_list.html", context)


@login_required
def airspace_class_detail(request, pk):
    """Display detailed view of airspace class"""
    airspace_class = get_object_or_404(AirspaceClass, pk=pk)

    # Get operational areas using this airspace class
    operational_areas = OperationalArea.objects.filter(
        airspace_class=airspace_class
    ).order_by("-created_at")[:10]

    context = {
        "airspace_class": airspace_class,
        "operational_areas": operational_areas,
    }
    return render(request, "airspace/airspace_class_detail.html", context)


@login_required
def airspace_class_create(request):
    """Create new airspace class"""
    if request.method == "POST":
        form = AirspaceClassForm(request.POST)
        if form.is_valid():
            airspace_class = form.save()
            messages.success(
                request, f"Airspace class '{airspace_class.name}' created successfully."
            )
            return redirect("airspace:airspace_class_detail", pk=airspace_class.pk)
    else:
        form = AirspaceClassForm()

    context = {"form": form, "title": "Create Airspace Class"}
    return render(request, "airspace/airspace_class_form.html", context)


@login_required
def airspace_class_update(request, pk):
    """Update existing airspace class"""
    airspace_class = get_object_or_404(AirspaceClass, pk=pk)

    if request.method == "POST":
        form = AirspaceClassForm(request.POST, instance=airspace_class)
        if form.is_valid():
            airspace_class = form.save()
            messages.success(
                request, f"Airspace class '{airspace_class.name}' updated successfully."
            )
            return redirect("airspace:airspace_class_detail", pk=airspace_class.pk)
    else:
        form = AirspaceClassForm(instance=airspace_class)

    context = {
        "form": form,
        "airspace_class": airspace_class,
        "title": "Update Airspace Class",
    }
    return render(request, "airspace/airspace_class_form.html", context)


@login_required
@require_http_methods(["DELETE"])
def airspace_class_delete(request, pk):
    """Delete airspace class (AJAX)"""
    airspace_class = get_object_or_404(AirspaceClass, pk=pk)

    # Check if airspace class is being used
    operational_area_count = OperationalArea.objects.filter(
        airspace_class=airspace_class
    ).count()

    if operational_area_count > 0:
        return JsonResponse(
            {
                "success": False,
                "message": f"Cannot delete airspace class. It is used by {operational_area_count} operational area(s).",
            },
            status=400,
        )

    try:
        class_name = airspace_class.name
        airspace_class.delete()
        return JsonResponse(
            {
                "success": True,
                "message": f"Airspace class '{class_name}' deleted successfully.",
            }
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error deleting airspace class: {str(e)}"},
            status=500,
        )


# OperationalArea Views
@login_required
def operational_area_list(request):
    """List all operational areas with search and filtering"""
    operational_areas = OperationalArea.objects.select_related("airspace_class").all()

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        operational_areas = operational_areas.filter(
            Q(area_id__icontains=search_query)
            | Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(controlling_authority__icontains=search_query)
        )

    # Filter by area type
    area_type = request.GET.get("area_type", "")
    if area_type:
        operational_areas = operational_areas.filter(area_type=area_type)

    # Filter by status
    status = request.GET.get("status", "")
    if status:
        operational_areas = operational_areas.filter(status=status)

    # Filter by airspace class
    airspace_class_id = request.GET.get("airspace_class", "")
    if airspace_class_id:
        operational_areas = operational_areas.filter(
            airspace_class_id=airspace_class_id
        )

    # Filter by authorization required
    auth_required = request.GET.get("auth_required", "")
    if auth_required == "true":
        operational_areas = operational_areas.filter(authorization_required=True)
    elif auth_required == "false":
        operational_areas = operational_areas.filter(authorization_required=False)

    # Pagination
    paginator = Paginator(operational_areas, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get filter choices for template
    area_type_choices = OperationalArea.AREA_TYPE_CHOICES
    status_choices = OperationalArea.STATUS_CHOICES
    airspace_classes = AirspaceClass.objects.all()

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "area_type": area_type,
        "status": status,
        "airspace_class_id": airspace_class_id,
        "auth_required": auth_required,
        "area_type_choices": area_type_choices,
        "status_choices": status_choices,
        "airspace_classes": airspace_classes,
    }
    return render(request, "airspace/operational_area_list.html", context)


@login_required
def operational_area_detail(request, pk):
    """Display detailed view of operational area"""
    operational_area = get_object_or_404(
        OperationalArea.objects.select_related("airspace_class"), pk=pk
    )

    context = {
        "operational_area": operational_area,
    }
    return render(request, "airspace/operational_area_detail.html", context)


@login_required
def operational_area_create(request):
    """Create new operational area"""
    if request.method == "POST":
        form = OperationalAreaForm(request.POST)
        if form.is_valid():
            operational_area = form.save()
            messages.success(
                request,
                f"Operational area '{operational_area.area_id}' created successfully.",
            )
            return redirect("airspace:operational_area_detail", pk=operational_area.pk)
    else:
        form = OperationalAreaForm()

    context = {"form": form, "title": "Create Operational Area"}
    return render(request, "airspace/operational_area_form.html", context)


@login_required
def operational_area_update(request, pk):
    """Update existing operational area"""
    operational_area = get_object_or_404(OperationalArea, pk=pk)

    if request.method == "POST":
        form = OperationalAreaForm(request.POST, instance=operational_area)
        if form.is_valid():
            operational_area = form.save()
            messages.success(
                request,
                f"Operational area '{operational_area.area_id}' updated successfully.",
            )
            return redirect("airspace:operational_area_detail", pk=operational_area.pk)
    else:
        form = OperationalAreaForm(instance=operational_area)

    context = {
        "form": form,
        "operational_area": operational_area,
        "title": "Update Operational Area",
    }
    return render(request, "airspace/operational_area_form.html", context)


@login_required
@require_http_methods(["DELETE"])
def operational_area_delete(request, pk):
    """Delete operational area (AJAX)"""
    operational_area = get_object_or_404(OperationalArea, pk=pk)

    try:
        area_id = operational_area.area_id
        operational_area.delete()
        return JsonResponse(
            {
                "success": True,
                "message": f"Operational area '{area_id}' deleted successfully.",
            }
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error deleting operational area: {str(e)}"},
            status=500,
        )


# AJAX Views for dynamic functionality
@login_required
def get_operational_areas_by_class(request):
    """Get operational areas filtered by airspace class (AJAX)"""
    airspace_class_id = request.GET.get("airspace_class_id")

    if not airspace_class_id:
        return JsonResponse({"areas": []})

    areas = OperationalArea.objects.filter(airspace_class_id=airspace_class_id).values(
        "id", "area_id", "name", "status"
    )

    return JsonResponse({"areas": list(areas)})


@login_required
def validate_area_id(request):
    """Validate area ID uniqueness (AJAX)"""
    area_id = request.GET.get("area_id", "").strip()
    exclude_pk = request.GET.get("exclude_pk")

    if not area_id:
        return JsonResponse({"valid": False, "message": "Area ID is required"})

    # Check format
    import re

    if not re.match(r"^OA-[A-Z0-9]{6,12}$", area_id):
        return JsonResponse(
            {
                "valid": False,
                "message": "Format: OA-XXXXXX (6-12 alphanumeric characters)",
            }
        )

    # Check uniqueness
    queryset = OperationalArea.objects.filter(area_id=area_id)
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)

    if queryset.exists():
        return JsonResponse(
            {"valid": False, "message": "This Area ID is already in use"}
        )

    return JsonResponse({"valid": True, "message": "Area ID is available"})
