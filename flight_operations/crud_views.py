from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    FlightLogForm,
    FlightPlanForm,
    JobSafetyAssessmentForm,
    MissionForm,
    RiskRegisterForm,
)
from .models import FlightLog, FlightPlan, JobSafetyAssessment, Mission, RiskRegister


@login_required
def flight_operations_dashboard(request):
    """Flight Operations dashboard with key metrics and recent activity"""

    # Key metrics
    total_missions = Mission.objects.count()
    active_missions = Mission.objects.filter(status="active").count()
    completed_missions = Mission.objects.filter(status="completed").count()
    total_flight_hours = (
        FlightLog.objects.aggregate(total_hours=Sum("flight_time"))["total_hours"] or 0
    )

    # Recent activity
    recent_missions = Mission.objects.select_related(
        "mission_commander", "client"
    ).order_by("-created_at")[:5]

    recent_flights = FlightLog.objects.select_related(
        "flight_plan__mission", "remote_pilot"
    ).order_by("-takeoff_time")[:5]

    pending_assessments = JobSafetyAssessment.objects.filter(
        flight_authorized=False
    ).count()

    high_risks = RiskRegister.objects.filter(risk_level="high").count()

    context = {
        "total_missions": total_missions,
        "active_missions": active_missions,
        "completed_missions": completed_missions,
        "total_flight_hours": round(float(total_flight_hours), 1),
        "recent_missions": recent_missions,
        "recent_flights": recent_flights,
        "pending_assessments": pending_assessments,
        "high_risks": high_risks,
        "now": timezone.now(),
    }

    return render(request, "flight_operations/dashboard.html", context)


# Mission CRUD Views
@login_required
def mission_list(request):
    """List all missions with filtering and search"""
    missions = Mission.objects.select_related("mission_commander", "client").order_by(
        "-created_at"
    )

    # Search functionality
    search = request.GET.get("search", "")
    if search:
        missions = missions.filter(
            Q(mission_id__icontains=search)
            | Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(mission_type__icontains=search)
        )

    # Filter by status
    status = request.GET.get("status", "")
    if status:
        missions = missions.filter(status=status)

    # Filter by priority
    priority = request.GET.get("priority", "")
    if priority:
        missions = missions.filter(priority=priority)

    # Filter by client
    client_id = request.GET.get("client", "")
    if client_id:
        missions = missions.filter(client_id=client_id)

    # Pagination
    paginator = Paginator(missions, 20)
    page_number = request.GET.get("page")
    missions = paginator.get_page(page_number)

    # Get choices for filters
    status_choices = Mission.STATUS_CHOICES
    priority_choices = Mission.PRIORITY_CHOICES

    context = {
        "missions": missions,
        "paginator": paginator,
        "search": search,
        "status": status,
        "priority": priority,
        "client_id": client_id,
        "status_choices": status_choices,
        "priority_choices": priority_choices,
    }

    return render(request, "flight_operations/mission_list.html", context)


@login_required
def mission_detail(request, pk):
    """Display detailed view of mission"""
    mission = get_object_or_404(
        Mission.objects.select_related("mission_commander", "client").prefetch_related(
            "flightplan_set", "riskregister_set", "jobsafetyassessment_set"
        ),
        pk=pk,
    )

    context = {
        "mission": mission,
    }
    return render(request, "flight_operations/mission_detail.html", context)


@login_required
def mission_create(request):
    """Create new mission"""
    if request.method == "POST":
        form = MissionForm(request.POST)
        if form.is_valid():
            mission = form.save()
            messages.success(
                request, f"Mission {mission.mission_id} created successfully!"
            )
            return redirect("flight_operations:mission_detail", pk=mission.pk)
    else:
        form = MissionForm()

    context = {
        "form": form,
        "title": "Create New Mission",
    }
    return render(request, "flight_operations/mission_form.html", context)


@login_required
def mission_update(request, pk):
    """Update existing mission"""
    mission = get_object_or_404(Mission, pk=pk)

    if request.method == "POST":
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Mission {mission.mission_id} updated successfully!"
            )
            return redirect("flight_operations:mission_detail", pk=mission.pk)
    else:
        form = MissionForm(instance=mission)

    context = {
        "form": form,
        "mission": mission,
        "title": "Edit Mission",
    }
    return render(request, "flight_operations/mission_form.html", context)


@login_required
def mission_delete(request, pk):
    """Delete mission"""
    mission = get_object_or_404(Mission, pk=pk)

    if request.method == "POST":
        mission_ref = mission.mission_id
        mission.delete()
        messages.success(request, f"Mission {mission_ref} deleted successfully!")
        return redirect("flight_operations:mission_list")

    context = {
        "mission": mission,
    }
    return render(request, "flight_operations/mission_delete.html", context)


# Flight Plan CRUD Views
@login_required
def flight_plan_list(request):
    """List all flight plans with filtering"""
    flight_plans = FlightPlan.objects.select_related(
        "mission", "aircraft", "pilot_in_command"
    ).order_by("-created_at")

    # Search functionality
    search = request.GET.get("search", "")
    if search:
        flight_plans = flight_plans.filter(
            Q(flight_plan_id__icontains=search)
            | Q(mission__mission_id__icontains=search)
            | Q(mission__name__icontains=search)
        )

    # Filter by mission
    mission_id = request.GET.get("mission", "")
    if mission_id:
        flight_plans = flight_plans.filter(mission_id=mission_id)

    # Filter by status
    status = request.GET.get("status", "")
    if status:
        flight_plans = flight_plans.filter(status=status)

    # Pagination
    paginator = Paginator(flight_plans, 15)
    page_number = request.GET.get("page")
    flight_plans = paginator.get_page(page_number)

    context = {
        "flight_plans": flight_plans,
        "paginator": paginator,
        "search": search,
        "mission_id": mission_id,
        "status": status,
    }

    return render(request, "flight_operations/flight_plan_list.html", context)


@login_required
def flight_plan_detail(request, pk):
    """Display detailed view of flight plan"""
    flight_plan = get_object_or_404(
        FlightPlan.objects.select_related(
            "mission", "aircraft", "pilot_in_command"
        ).prefetch_related("flight_logs"),
        pk=pk,
    )

    context = {
        "flight_plan": flight_plan,
    }
    return render(request, "flight_operations/flight_plan_detail.html", context)


@login_required
def flight_plan_create(request):
    """Create new flight plan"""
    mission_id = request.GET.get("mission")
    initial_data = {}

    if mission_id:
        try:
            mission = Mission.objects.get(pk=mission_id)
            initial_data["mission"] = mission
        except Mission.DoesNotExist:
            pass

    if request.method == "POST":
        form = FlightPlanForm(request.POST)
        if form.is_valid():
            flight_plan = form.save()
            messages.success(
                request,
                f"Flight Plan {flight_plan.flight_plan_id} created successfully!",
            )
            return redirect("flight_operations:flight_plan_detail", pk=flight_plan.pk)
    else:
        form = FlightPlanForm(initial=initial_data)

    context = {
        "form": form,
        "title": "Create New Flight Plan",
    }
    return render(request, "flight_operations/flight_plan_form.html", context)


@login_required
def flight_plan_update(request, pk):
    """Update existing flight plan"""
    flight_plan = get_object_or_404(FlightPlan, pk=pk)

    if request.method == "POST":
        form = FlightPlanForm(request.POST, instance=flight_plan)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Flight Plan {flight_plan.flight_plan_id} updated successfully!",
            )
            return redirect("flight_operations:flight_plan_detail", pk=flight_plan.pk)
    else:
        form = FlightPlanForm(instance=flight_plan)

    context = {
        "form": form,
        "flight_plan": flight_plan,
        "title": "Edit Flight Plan",
    }
    return render(request, "flight_operations/flight_plan_form.html", context)


# Flight Log CRUD Views
@login_required
def flight_log_list(request):
    """List all flight logs"""
    flight_logs = FlightLog.objects.select_related(
        "flight_plan__mission", "remote_pilot", "aircraft"
    ).order_by("-takeoff_time")

    # Search functionality
    search = request.GET.get("search", "")
    if search:
        flight_logs = flight_logs.filter(
            Q(flight_plan__flight_plan_id__icontains=search)
            | Q(flight_plan__mission__mission_id__icontains=search)
            | Q(remote_pilot__user__first_name__icontains=search)
            | Q(remote_pilot__user__last_name__icontains=search)
        )

    # Filter by date range
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    if date_from:
        flight_logs = flight_logs.filter(takeoff_time__date__gte=date_from)
    if date_to:
        flight_logs = flight_logs.filter(takeoff_time__date__lte=date_to)

    # Pagination
    paginator = Paginator(flight_logs, 20)
    page_number = request.GET.get("page")
    flight_logs = paginator.get_page(page_number)

    context = {
        "flight_logs": flight_logs,
        "paginator": paginator,
        "search": search,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render(request, "flight_operations/flight_log_list.html", context)


@login_required
def flight_log_detail(request, pk):
    """Display detailed view of flight log"""
    flight_log = get_object_or_404(
        FlightLog.objects.select_related(
            "flight_plan__mission", "remote_pilot", "aircraft"
        ),
        pk=pk,
    )

    context = {
        "flight_log": flight_log,
    }
    return render(request, "flight_operations/flight_log_detail.html", context)


@login_required
def flight_log_create(request):
    """Create new flight log"""
    flight_plan_id = request.GET.get("flight_plan")
    initial_data = {}

    if flight_plan_id:
        try:
            flight_plan = FlightPlan.objects.get(pk=flight_plan_id)
            initial_data["flight_plan"] = flight_plan
            initial_data["aircraft"] = flight_plan.aircraft
            initial_data["remote_pilot"] = flight_plan.pilot_in_command
        except FlightPlan.DoesNotExist:
            pass

    if request.method == "POST":
        form = FlightLogForm(request.POST)
        if form.is_valid():
            flight_log = form.save()
            messages.success(request, f"Flight Log created successfully!")
            return redirect("flight_operations:flight_log_detail", pk=flight_log.pk)
    else:
        form = FlightLogForm(initial=initial_data)

    context = {
        "form": form,
        "title": "Create New Flight Log",
    }
    return render(request, "flight_operations/flight_log_form.html", context)


# Risk Register CRUD Views
@login_required
def risk_register_list(request):
    """List all risk register entries"""
    risks = RiskRegister.objects.select_related("mission").order_by("-date_entered")

    # Filter by mission
    mission_id = request.GET.get("mission", "")
    if mission_id:
        risks = risks.filter(mission_id=mission_id)

    # Filter by risk level
    risk_level = request.GET.get("risk_level", "")
    if risk_level:
        risks = risks.filter(risk_level=risk_level)

    # Pagination
    paginator = Paginator(risks, 15)
    page_number = request.GET.get("page")
    risks = paginator.get_page(page_number)

    context = {
        "risks": risks,
        "paginator": paginator,
        "mission_id": mission_id,
        "risk_level": risk_level,
    }

    return render(request, "flight_operations/risk_register_list.html", context)


@login_required
def risk_register_create(request):
    """Create new risk register entry"""
    mission_id = request.GET.get("mission")
    initial_data = {}

    if mission_id:
        try:
            mission = Mission.objects.get(pk=mission_id)
            initial_data["mission"] = mission
        except Mission.DoesNotExist:
            pass

    if request.method == "POST":
        form = RiskRegisterForm(request.POST)
        if form.is_valid():
            risk = form.save()
            messages.success(
                request, f"Risk Register {risk.reference_number} created successfully!"
            )
            return redirect("flight_operations:mission_detail", pk=risk.mission.pk)
    else:
        form = RiskRegisterForm(initial=initial_data)

    context = {
        "form": form,
        "title": "Create Risk Register Entry",
    }
    return render(request, "flight_operations/risk_register_form.html", context)


# Job Safety Assessment CRUD Views
@login_required
def jsa_list(request):
    """List all Job Safety Assessments"""
    assessments = JobSafetyAssessment.objects.select_related("mission").order_by(
        "-created_at"
    )

    # Filter by approval status
    status = request.GET.get("status", "")
    if status:
        if status == "approved":
            assessments = assessments.filter(flight_authorized=True)
        elif status == "pending":
            assessments = assessments.filter(flight_authorized=False)

    # Pagination
    paginator = Paginator(assessments, 15)
    page_number = request.GET.get("page")
    assessments = paginator.get_page(page_number)

    context = {
        "assessments": assessments,
        "paginator": paginator,
        "status": status,
    }

    return render(request, "flight_operations/jsa_list.html", context)


@login_required
def jsa_create(request):
    """Create new Job Safety Assessment"""
    mission_id = request.GET.get("mission")
    initial_data = {}

    if mission_id:
        try:
            mission = Mission.objects.get(pk=mission_id)
            initial_data["mission"] = mission
        except Mission.DoesNotExist:
            pass

    if request.method == "POST":
        form = JobSafetyAssessmentForm(request.POST)
        if form.is_valid():
            jsa = form.save()
            messages.success(request, f"Job Safety Assessment created successfully!")
            return redirect("flight_operations:mission_detail", pk=jsa.mission.pk)
    else:
        form = JobSafetyAssessmentForm(initial=initial_data)

    context = {
        "form": form,
        "title": "Create Job Safety Assessment",
    }
    return render(request, "flight_operations/jsa_form.html", context)


# AJAX Functions
@login_required
def ajax_mission_delete(request, pk):
    """AJAX delete mission"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        mission = Mission.objects.get(pk=pk)
        mission_ref = mission.mission_id
        title = mission.name
        mission.delete()

        return JsonResponse(
            {
                "success": True,
                "message": f"Mission {mission_ref} - {title} deleted successfully",
            }
        )
    except Mission.DoesNotExist:
        return JsonResponse({"success": False, "error": "Mission not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def ajax_flight_plan_delete(request, pk):
    """AJAX delete flight plan"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        flight_plan = FlightPlan.objects.get(pk=pk)
        flight_ref = flight_plan.flight_plan_id
        flight_plan.delete()

        return JsonResponse(
            {
                "success": True,
                "message": f"Flight Plan {flight_ref} deleted successfully",
            }
        )
    except FlightPlan.DoesNotExist:
        return JsonResponse({"success": False, "error": "Flight Plan not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def ajax_dashboard_stats(request):
    """Get dashboard statistics for AJAX refresh"""
    try:
        stats = {
            "total_missions": Mission.objects.count(),
            "active_missions": Mission.objects.filter(status="active").count(),
            "completed_missions": Mission.objects.filter(status="completed").count(),
            "total_flight_hours": 0,  # Will be calculated separately
            "pending_assessments": JobSafetyAssessment.objects.filter(
                flight_authorized=False
            ).count(),
            "high_risks": RiskRegister.objects.filter(risk_level="high").count(),
        }

        return JsonResponse({"success": True, "stats": stats})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
