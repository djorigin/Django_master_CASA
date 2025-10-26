from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import (
    RPASOperationsManualForm,
    SOPProcedureStepForm,
    StandardOperatingProcedureForm,
    TrainingSyllabusForm,
)
from .models import (
    RPASOperationsManual,
    SOPProcedureStep,
    StandardOperatingProcedure,
    TrainingSyllabus,
)


@login_required
def core_dashboard(request):
    """Main core management dashboard with statistics"""
    total_sops = StandardOperatingProcedure.objects.count()
    approved_sops = StandardOperatingProcedure.objects.filter(status="approved").count()
    draft_sops = StandardOperatingProcedure.objects.filter(status="draft").count()

    # SOPs by category
    sop_category_breakdown = {}
    for category_choice in StandardOperatingProcedure.CATEGORY_CHOICES:
        category_code = category_choice[0]
        sop_category_breakdown[category_choice[1]] = (
            StandardOperatingProcedure.objects.filter(category=category_code).count()
        )

    # SOPs by status
    sop_status_breakdown = {}
    for status_choice in StandardOperatingProcedure.STATUS_CHOICES:
        status_code = status_choice[0]
        sop_status_breakdown[status_choice[1]] = (
            StandardOperatingProcedure.objects.filter(status=status_code).count()
        )

    # Recent SOPs
    recent_sops = StandardOperatingProcedure.objects.order_by("-created_date")[:5]

    # Training statistics
    total_syllabuses = TrainingSyllabus.objects.count()
    active_syllabuses = TrainingSyllabus.objects.filter(status="active").count()

    # Operations manuals
    total_manuals = RPASOperationsManual.objects.count()
    approved_manuals = RPASOperationsManual.objects.filter(status="approved").count()

    # Overdue reviews
    overdue_sops = StandardOperatingProcedure.objects.filter(
        next_review_date__lt=timezone.now().date(), status="approved"
    ).count()

    context = {
        "total_sops": total_sops,
        "approved_sops": approved_sops,
        "draft_sops": draft_sops,
        "sop_category_breakdown": sop_category_breakdown,
        "sop_status_breakdown": sop_status_breakdown,
        "recent_sops": recent_sops,
        "total_syllabuses": total_syllabuses,
        "active_syllabuses": active_syllabuses,
        "total_manuals": total_manuals,
        "approved_manuals": approved_manuals,
        "overdue_sops": overdue_sops,
    }
    return render(request, "core/dashboard.html", context)


# StandardOperatingProcedure Views
@login_required
def sop_list(request):
    """List all Standard Operating Procedures with search and filtering"""
    sops = StandardOperatingProcedure.objects.select_related(
        "created_by", "approved_by", "reviewed_by"
    ).prefetch_related("aircraft_types")

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        sops = sops.filter(
            Q(sop_id__icontains=search_query)
            | Q(title__icontains=search_query)
            | Q(purpose__icontains=search_query)
            | Q(scope__icontains=search_query)
        )

    # Filter by category
    category = request.GET.get("category", "")
    if category:
        sops = sops.filter(category=category)

    # Filter by status
    status = request.GET.get("status", "")
    if status:
        sops = sops.filter(status=status)

    # Filter by priority
    priority = request.GET.get("priority", "")
    if priority:
        sops = sops.filter(priority=priority)

    # Filter by overdue review
    overdue_review = request.GET.get("overdue_review", "")
    if overdue_review == "true":
        sops = sops.filter(
            next_review_date__lt=timezone.now().date(), status="approved"
        )

    # Pagination
    paginator = Paginator(sops, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get filter choices for template
    category_choices = StandardOperatingProcedure.CATEGORY_CHOICES
    status_choices = StandardOperatingProcedure.STATUS_CHOICES
    priority_choices = StandardOperatingProcedure.PRIORITY_CHOICES

    context = {
        "page_obj": page_obj,
        "sops": page_obj,  # Template expects 'sops' - adding alias for compatibility
        "search_query": search_query,
        "category": category,
        "status": status,
        "priority": priority,
        "overdue_review": overdue_review,
        "category_choices": category_choices,
        "status_choices": status_choices,
        "priority_choices": priority_choices,
    }
    return render(request, "core/sop_list.html", context)


@login_required
def sop_detail(request, pk):
    """Display detailed view of Standard Operating Procedure"""
    sop = get_object_or_404(
        StandardOperatingProcedure.objects.select_related(
            "created_by", "approved_by", "reviewed_by", "superseded_by", "supersedes"
        ).prefetch_related("aircraft_types", "procedure_steps"),
        pk=pk,
    )

    # Get procedure steps ordered by step number
    procedure_steps = sop.procedure_steps.order_by("step_number")

    context = {
        "sop": sop,
        "procedure_steps": procedure_steps,
    }
    return render(request, "core/sop_detail.html", context)


@login_required
def sop_create(request):
    """Create new Standard Operating Procedure"""
    if request.method == "POST":
        form = StandardOperatingProcedureForm(request.POST)
        if form.is_valid():
            try:
                # Check if user has proper access (staff profile required even for superusers for audit trail)
                if (
                    hasattr(request.user, 'staff_profile')
                    and request.user.staff_profile
                ):
                    sop = form.save(commit=False)
                    sop.created_by = request.user.staff_profile
                    sop.save()

                    # Different success message for superusers
                    if request.user.is_superuser:
                        messages.success(
                            request,
                            f"SOP '{sop.sop_id}' created successfully (Administrator access).",
                        )
                    else:
                        messages.success(
                            request, f"SOP '{sop.sop_id}' created successfully."
                        )

                    return redirect("core:sop_detail", pk=sop.pk)
                else:
                    # Handle different error messages for superuser vs regular user
                    if request.user.is_superuser:
                        messages.error(
                            request,
                            "Administrator Profile Required - Please create a Staff Profile for your administrator account to maintain proper audit trails for SOPs.",
                        )
                    else:
                        messages.error(
                            request,
                            "SOP Creation Error - User Not Authorised. Staff profile required to create SOPs.",
                        )
                    return render(
                        request,
                        "core/sop_form.html",
                        {"form": form, "title": "Create Standard Operating Procedure"},
                    )
            except AttributeError:
                # Catch any attribute errors gracefully
                messages.error(
                    request,
                    "SOP Creation Error - User Not Authorised. Please contact administrator.",
                )
                return render(
                    request,
                    "core/sop_form.html",
                    {"form": form, "title": "Create Standard Operating Procedure"},
                )
    else:
        form = StandardOperatingProcedureForm()

    context = {"form": form, "title": "Create Standard Operating Procedure"}
    return render(request, "core/sop_form.html", context)


@login_required
def sop_update(request, pk):
    """Update existing Standard Operating Procedure"""
    sop = get_object_or_404(StandardOperatingProcedure, pk=pk)

    if request.method == "POST":
        form = StandardOperatingProcedureForm(request.POST, instance=sop)
        if form.is_valid():
            sop = form.save()
            messages.success(request, f"SOP '{sop.sop_id}' updated successfully.")
            return redirect("core:sop_detail", pk=sop.pk)
    else:
        form = StandardOperatingProcedureForm(instance=sop)

    context = {
        "form": form,
        "sop": sop,
        "title": "Update Standard Operating Procedure",
    }
    return render(request, "core/sop_form.html", context)


@login_required
@require_http_methods(["DELETE"])
def sop_delete(request, pk):
    """Delete Standard Operating Procedure (AJAX)"""
    sop = get_object_or_404(StandardOperatingProcedure, pk=pk)

    # Check if SOP can be safely deleted
    if sop.status == "approved" and sop.procedure_steps.exists():
        return JsonResponse(
            {
                "success": False,
                "message": f"Cannot delete approved SOP '{sop.sop_id}' with procedure steps. Consider superseding it instead.",
            },
            status=400,
        )

    try:
        sop_id = sop.sop_id
        sop.delete()
        return JsonResponse(
            {"success": True, "message": f"SOP '{sop_id}' deleted successfully."}
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error deleting SOP: {str(e)}"}, status=500
        )


# SOP Procedure Step Views
@login_required
def sop_step_create(request, sop_pk):
    """Create new procedure step for SOP"""
    sop = get_object_or_404(StandardOperatingProcedure, pk=sop_pk)

    if request.method == "POST":
        form = SOPProcedureStepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.sop = sop
            step.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(
                request, f"Procedure step {step.step_number} created successfully."
            )
            return redirect("core:sop_steps_list", sop_pk=sop.pk)
    else:
        # Auto-increment step number
        last_step = sop.procedure_steps.order_by("step_number").last()
        next_step_number = (last_step.step_number + 1) if last_step else 1
        form = SOPProcedureStepForm(initial={"step_number": next_step_number})

    context = {
        "form": form,
        "sop": sop,
        "title": f"Add Step to {sop.sop_id}",
    }
    return render(request, "core/sop_step_form.html", context)


@login_required
def sop_step_update(request, sop_pk, step_pk):
    """Update existing procedure step"""
    sop = get_object_or_404(StandardOperatingProcedure, pk=sop_pk)
    step = get_object_or_404(SOPProcedureStep, pk=step_pk, sop=sop)

    if request.method == "POST":
        form = SOPProcedureStepForm(request.POST, instance=step)
        if form.is_valid():
            step = form.save()
            messages.success(
                request, f"Procedure step {step.step_number} updated successfully."
            )
            return redirect("core:sop_detail", pk=sop.pk)
    else:
        form = SOPProcedureStepForm(instance=step)

    context = {
        "form": form,
        "sop": sop,
        "step": step,
        "title": f"Update Step {step.step_number}",
    }
    return render(request, "core/sop_step_form.html", context)


@login_required
@require_http_methods(["DELETE"])
def sop_step_delete(request, sop_pk, step_pk):
    """Delete procedure step (AJAX)"""
    sop = get_object_or_404(StandardOperatingProcedure, pk=sop_pk)
    step = get_object_or_404(SOPProcedureStep, pk=step_pk, sop=sop)

    try:
        step_number = step.step_number
        step.delete()
        return JsonResponse(
            {"success": True, "message": f"Step {step_number} deleted successfully."}
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error deleting step: {str(e)}"}, status=500
        )


# Training Syllabus Views
@login_required
def training_syllabus_list(request):
    """List all training syllabuses with search and filtering"""
    syllabuses = TrainingSyllabus.objects.select_related("created_by", "approved_by")

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        syllabuses = syllabuses.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(learning_objectives__icontains=search_query)
        )

    # Filter by training category
    training_category = request.GET.get("training_category", "")
    if training_category:
        syllabuses = syllabuses.filter(training_category=training_category)

    # Filter by status
    status = request.GET.get("status", "")
    if status:
        syllabuses = syllabuses.filter(status=status)

    # Pagination
    paginator = Paginator(syllabuses, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get filter choices for template
    training_category_choices = TrainingSyllabus.TRAINING_CATEGORY_CHOICES
    status_choices = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("under_review", "Under Review"),
        ("superseded", "Superseded"),
    ]

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "training_category": training_category,
        "status": status,
        "training_category_choices": training_category_choices,
        "status_choices": status_choices,
    }
    return render(request, "core/training_syllabus_list.html", context)


@login_required
def training_syllabus_detail(request, pk):
    """Display detailed view of training syllabus"""
    syllabus = get_object_or_404(
        TrainingSyllabus.objects.select_related("created_by", "approved_by"), pk=pk
    )

    context = {
        "syllabus": syllabus,
    }
    return render(request, "core/training_syllabus_detail.html", context)


@login_required
def training_syllabus_create(request):
    """Create new training syllabus"""
    if request.method == "POST":
        form = TrainingSyllabusForm(request.POST)
        if form.is_valid():
            syllabus = form.save(commit=False)
            syllabus.created_by = request.user.staffprofile
            syllabus = form.save()
            messages.success(
                request, f"Training syllabus '{syllabus.title}' created successfully."
            )
            return redirect("core:training_syllabus_detail", pk=syllabus.pk)
    else:
        form = TrainingSyllabusForm()

    context = {"form": form, "title": "Create Training Syllabus"}
    return render(request, "core/training_syllabus_form.html", context)


@login_required
def training_syllabus_update(request, pk):
    """Update existing training syllabus"""
    syllabus = get_object_or_404(TrainingSyllabus, pk=pk)

    if request.method == "POST":
        form = TrainingSyllabusForm(request.POST, instance=syllabus)
        if form.is_valid():
            syllabus = form.save()
            messages.success(
                request, f"Training syllabus '{syllabus.title}' updated successfully."
            )
            return redirect("core:training_syllabus_detail", pk=syllabus.pk)
    else:
        form = TrainingSyllabusForm(instance=syllabus)

    context = {
        "form": form,
        "syllabus": syllabus,
        "title": "Update Training Syllabus",
    }
    return render(request, "core/training_syllabus_form.html", context)


@login_required
@require_http_methods(["DELETE"])
def training_syllabus_delete(request, pk):
    """Delete training syllabus (AJAX)"""
    syllabus = get_object_or_404(TrainingSyllabus, pk=pk)

    try:
        title = syllabus.title
        syllabus.delete()
        return JsonResponse(
            {
                "success": True,
                "message": f"Training syllabus '{title}' deleted successfully.",
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": f"Error deleting training syllabus: {str(e)}",
            },
            status=500,
        )


# RPAS Operations Manual Views
@login_required
def operations_manual_list(request):
    """List all RPAS Operations Manuals with search and filtering"""
    manuals = RPASOperationsManual.objects.select_related("created_by", "approved_by")

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        manuals = manuals.filter(
            Q(manual_id__icontains=search_query)
            | Q(title__icontains=search_query)
            | Q(organization_name__icontains=search_query)
        )

    # Filter by approval status
    approval_status = request.GET.get("approval_status", "")
    if approval_status:
        manuals = manuals.filter(status=approval_status)

    # Filter by manual type
    manual_type = request.GET.get("manual_type", "")
    if manual_type:
        manuals = manuals.filter(manual_type=manual_type)

    # Pagination
    paginator = Paginator(manuals, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get filter choices for template
    approval_status_choices = [
        ("draft", "Draft"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("requires_revision", "Requires Revision"),
        ("superseded", "Superseded"),
    ]
    manual_type_choices = [
        ("operations", "Operations Manual"),
        ("maintenance", "Maintenance Manual"),
        ("training", "Training Manual"),
        ("emergency", "Emergency Procedures"),
    ]

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "approval_status": approval_status,
        "manual_type": manual_type,
        "approval_status_choices": approval_status_choices,
        "manual_type_choices": manual_type_choices,
    }
    return render(request, "core/operations_manual_list.html", context)


@login_required
def operations_manual_detail(request, pk):
    """Display detailed view of RPAS Operations Manual"""
    manual = get_object_or_404(
        RPASOperationsManual.objects.select_related(
            "created_by", "approved_by"
        ).prefetch_related("sections"),
        pk=pk,
    )

    context = {
        "manual": manual,
    }
    return render(request, "core/operations_manual_detail.html", context)


@login_required
def operations_manual_create(request):
    """Create new RPAS Operations Manual"""
    if request.method == "POST":
        form = RPASOperationsManualForm(request.POST)
        if form.is_valid():
            manual = form.save(commit=False)
            manual.created_by = request.user.staffprofile
            manual = form.save()
            messages.success(
                request, f"Operations manual '{manual.manual_id}' created successfully."
            )
            return redirect("core:operations_manual_detail", pk=manual.pk)
    else:
        form = RPASOperationsManualForm()

    context = {"form": form, "title": "Create RPAS Operations Manual"}
    return render(request, "core/operations_manual_form.html", context)


@login_required
def operations_manual_update(request, pk):
    """Update existing RPAS Operations Manual"""
    manual = get_object_or_404(RPASOperationsManual, pk=pk)

    if request.method == "POST":
        form = RPASOperationsManualForm(request.POST, instance=manual)
        if form.is_valid():
            manual = form.save()
            messages.success(
                request, f"Operations manual '{manual.manual_id}' updated successfully."
            )
            return redirect("core:operations_manual_detail", pk=manual.pk)
    else:
        form = RPASOperationsManualForm(instance=manual)

    context = {
        "form": form,
        "manual": manual,
        "title": "Update RPAS Operations Manual",
    }
    return render(request, "core/operations_manual_form.html", context)


@login_required
@require_http_methods(["DELETE"])
def operations_manual_delete(request, pk):
    """Delete RPAS Operations Manual (AJAX)"""
    manual = get_object_or_404(RPASOperationsManual, pk=pk)

    try:
        manual_id = manual.manual_id
        manual.delete()
        return JsonResponse(
            {
                "success": True,
                "message": f"Operations manual '{manual_id}' deleted successfully.",
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": f"Error deleting operations manual: {str(e)}",
            },
            status=500,
        )


# AJAX Views for dynamic functionality
@login_required
def get_sops_by_category(request):
    """Get SOPs filtered by category (AJAX)"""
    category = request.GET.get("category")

    if not category:
        return JsonResponse({"sops": []})

    sops = StandardOperatingProcedure.objects.filter(category=category).values(
        "id", "sop_id", "title", "status"
    )

    return JsonResponse({"sops": list(sops)})


@login_required
def validate_sop_id(request):
    """Validate SOP ID uniqueness (AJAX)"""
    sop_id = request.GET.get("sop_id", "").strip().upper()
    exclude_pk = request.GET.get("exclude_pk")

    if not sop_id:
        return JsonResponse({"valid": False, "message": "SOP ID is required"})

    # Check format
    import re

    if not re.match(r"^[A-Z]{3}-\d{3}-SOP$", sop_id):
        return JsonResponse(
            {
                "valid": False,
                "message": "Format must be XXX-XXX-SOP (e.g., FLT-001-SOP)",
            }
        )

    # Check uniqueness
    queryset = StandardOperatingProcedure.objects.filter(sop_id=sop_id)
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)

    if queryset.exists():
        return JsonResponse(
            {"valid": False, "message": "This SOP ID is already in use"}
        )

    return JsonResponse({"valid": True, "message": "SOP ID is available"})


# SOP Steps Management Functions
@login_required
def sop_steps_list(request, sop_pk):
    """List procedure steps for a specific SOP"""
    sop = get_object_or_404(StandardOperatingProcedure, pk=sop_pk)
    steps = SOPProcedureStep.objects.filter(sop=sop).order_by('step_number')

    context = {
        "sop": sop,
        "steps": steps,
    }
    return render(request, "core/sop_steps_list.html", context)


# Duplicate function removed - using the version with auto-increment logic above


@login_required
def sop_step_update(request, sop_pk, pk):
    """Update SOP procedure step"""
    sop = get_object_or_404(StandardOperatingProcedure, pk=sop_pk)
    step = get_object_or_404(SOPProcedureStep, pk=pk, sop=sop)

    if request.method == "POST":
        form = SOPProcedureStepForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Procedure step {step.step_number} updated successfully!"
            )
            return redirect("core:sop_steps_list", sop_pk=sop.pk)
    else:
        form = SOPProcedureStepForm(instance=step)

    context = {
        "form": form,
        "sop": sop,
        "step": step,
        "title": "Edit SOP Step",
    }
    return render(request, "core/sop_step_form.html", context)


@login_required
def sop_step_delete(request, sop_pk, pk):
    """Delete SOP procedure step"""
    sop = get_object_or_404(StandardOperatingProcedure, pk=sop_pk)
    step = get_object_or_404(SOPProcedureStep, pk=pk, sop=sop)

    if request.method == "POST":
        step_number = step.step_number
        step.delete()
        messages.success(request, f"Procedure step {step_number} deleted successfully!")
        return redirect("core:sop_steps_list", sop_pk=sop.pk)

    context = {
        "sop": sop,
        "step": step,
    }
    return render(request, "core/sop_step_delete.html", context)


@login_required
def ajax_sop_step_delete(request, pk):
    """AJAX delete SOP procedure step"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        step = SOPProcedureStep.objects.get(pk=pk)
        step_number = step.step_number
        sop_id = step.sop.sop_id
        step.delete()

        return JsonResponse(
            {
                "success": True,
                "message": f"Step {step_number} from {sop_id} deleted successfully",
            }
        )
    except SOPProcedureStep.DoesNotExist:
        return JsonResponse({"success": False, "error": "Procedure step not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# Export Functions
@login_required
def sop_export(request, pk):
    """Export SOP as PDF or other format"""
    from django.http import HttpResponse

    sop = get_object_or_404(StandardOperatingProcedure, pk=pk)

    # For now, return a simple text export
    # In production, you would use a PDF generation library
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{sop.sop_id}_export.txt"'

    content = f"""
Standard Operating Procedure Export
===================================

SOP ID: {sop.sop_id}
Title: {sop.title}
Category: {sop.get_category_display()}
Version: {sop.version}
Status: {sop.get_status_display()}

Purpose:
{sop.purpose}

Scope:
{sop.scope}

Responsibilities:
{sop.responsibilities}

Created: {sop.created_at}
Last Updated: {sop.updated_at}
"""

    response.write(content)
    return response


@login_required
def training_syllabus_export(request, pk):
    """Export Training Syllabus as PDF or other format"""
    from django.http import HttpResponse

    syllabus = get_object_or_404(TrainingSyllabus, pk=pk)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        f'attachment; filename="{syllabus.syllabus_id}_export.txt"'
    )

    content = f"""
Training Syllabus Export
========================

Syllabus ID: {syllabus.syllabus_id}
Title: {syllabus.title}
Category: {syllabus.get_category_display()}
Type: {syllabus.get_training_type_display()}
Status: {syllabus.get_status_display()}

Description:
{syllabus.description}

Learning Objectives:
{syllabus.learning_objectives}

Duration: {syllabus.duration_hours} hours
Theory: {syllabus.theory_hours} hours
Practical: {syllabus.practical_hours} hours

Assessment Method: {syllabus.assessment_method}
Pass Mark: {syllabus.pass_mark}%

Created: {syllabus.created_at}
Last Updated: {syllabus.updated_at}
"""

    response.write(content)
    return response


@login_required
def operations_manual_export(request, pk):
    """Export Operations Manual as PDF or other format"""
    from django.http import HttpResponse

    manual = get_object_or_404(RPASOperationsManual, pk=pk)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        f'attachment; filename="{manual.manual_id}_export.txt"'
    )

    content = f"""
RPAS Operations Manual Export
=============================

Manual ID: {manual.manual_id}
Title: {manual.title}
Type: {manual.get_manual_type_display()}
Version: {manual.version}
Status: {manual.get_status_display()}

Organization: {manual.organization_name}
ReOC Number: {manual.reoc_number}

Purpose and Scope:
{manual.purpose}

Abstract:
{manual.abstract}

Applicable Regulations:
{manual.applicable_regulations}

Effective Date: {manual.effective_date}
Next Review Date: {manual.next_review_date}

Created: {manual.created_at}
Last Updated: {manual.updated_at}
"""

    response.write(content)
    return response


# AJAX Quick Info Functions
@login_required
def ajax_sop_quick_info(request, pk):
    """Get quick SOP information for AJAX requests"""
    try:
        sop = StandardOperatingProcedure.objects.get(pk=pk)
        data = {
            "success": True,
            "sop_id": sop.sop_id,
            "title": sop.title,
            "category": sop.get_category_display(),
            "status": sop.get_status_display(),
            "version": sop.version,
            "purpose": (
                sop.purpose[:200] + "..." if len(sop.purpose) > 200 else sop.purpose
            ),
        }
    except StandardOperatingProcedure.DoesNotExist:
        data = {"success": False, "error": "SOP not found"}

    return JsonResponse(data)


@login_required
def ajax_training_syllabus_quick_info(request, pk):
    """Get quick training syllabus information for AJAX requests"""
    try:
        syllabus = TrainingSyllabus.objects.get(pk=pk)
        data = {
            "success": True,
            "syllabus_id": syllabus.syllabus_id,
            "title": syllabus.title,
            "category": syllabus.get_category_display(),
            "status": syllabus.get_status_display(),
            "duration_hours": str(syllabus.duration_hours),
            "description": (
                syllabus.description[:200] + "..."
                if len(syllabus.description) > 200
                else syllabus.description
            ),
        }
    except TrainingSyllabus.DoesNotExist:
        data = {"success": False, "error": "Training syllabus not found"}

    return JsonResponse(data)


@login_required
def ajax_operations_manual_quick_info(request, pk):
    """Get quick operations manual information for AJAX requests"""
    try:
        manual = RPASOperationsManual.objects.get(pk=pk)
        data = {
            "success": True,
            "manual_id": manual.manual_id,
            "title": manual.title,
            "manual_type": manual.get_manual_type_display(),
            "status": manual.get_status_display(),
            "version": manual.version,
            "organization": manual.organization_name,
        }
    except RPASOperationsManual.DoesNotExist:
        data = {"success": False, "error": "Operations manual not found"}

    return JsonResponse(data)


# AJAX Delete Functions
@login_required
def ajax_sop_delete(request, pk):
    """AJAX delete Standard Operating Procedure"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        sop = StandardOperatingProcedure.objects.get(pk=pk)
        sop_id = sop.sop_id
        title = sop.title
        sop.delete()

        return JsonResponse(
            {"success": True, "message": f"SOP {sop_id} - {title} deleted successfully"}
        )
    except StandardOperatingProcedure.DoesNotExist:
        return JsonResponse({"success": False, "error": "SOP not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def ajax_training_syllabus_delete(request, pk):
    """AJAX delete Training Syllabus"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        syllabus = TrainingSyllabus.objects.get(pk=pk)
        syllabus_id = syllabus.syllabus_id
        title = syllabus.title
        syllabus.delete()

        return JsonResponse(
            {
                "success": True,
                "message": f"Training Syllabus {syllabus_id} - {title} deleted successfully",
            }
        )
    except TrainingSyllabus.DoesNotExist:
        return JsonResponse({"success": False, "error": "Training syllabus not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def ajax_operations_manual_delete(request, pk):
    """AJAX delete Operations Manual"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        manual = RPASOperationsManual.objects.get(pk=pk)
        manual_id = manual.manual_id
        title = manual.title
        manual.delete()

        return JsonResponse(
            {
                "success": True,
                "message": f"Operations Manual {manual_id} - {title} deleted successfully",
            }
        )
    except RPASOperationsManual.DoesNotExist:
        return JsonResponse({"success": False, "error": "Operations manual not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# Dashboard Stats AJAX Function
@login_required
def ajax_dashboard_stats(request):
    """Get dashboard statistics for AJAX refresh"""
    try:
        stats = {
            "total_sops": StandardOperatingProcedure.objects.count(),
            "total_training": TrainingSyllabus.objects.count(),
            "total_manuals": RPASOperationsManual.objects.count(),
            "pending_approvals": (
                StandardOperatingProcedure.objects.filter(status="under_review").count()
                + TrainingSyllabus.objects.filter(status="draft").count()
                + RPASOperationsManual.objects.filter(status="review").count()
            ),
        }

        return JsonResponse({"success": True, "stats": stats})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
