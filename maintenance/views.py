from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import (
    MaintenanceCompletionForm,
    MaintenanceRecordForm,
    MaintenanceTypeForm,
    RPASMaintenanceEntryForm,
    RPASTechnicalLogPartAForm,
    RPASTechnicalLogPartBForm,
)
from .models import (
    MaintenanceRecord,
    MaintenanceType,
    RPASMaintenanceEntry,
    RPASTechnicalLogPartA,
    RPASTechnicalLogPartB,
)


@login_required
def maintenance_dashboard(request):
    """Main maintenance management dashboard with statistics"""
    # Basic statistics
    total_maintenance_records = MaintenanceRecord.objects.count()
    active_maintenance = MaintenanceRecord.objects.filter(
        status__in=['scheduled', 'in_progress']
    ).count()
    completed_maintenance = MaintenanceRecord.objects.filter(status='completed').count()
    overdue_maintenance = MaintenanceRecord.objects.filter(
        scheduled_date__lt=timezone.now().date(), status='scheduled'
    ).count()

    # Maintenance by status
    maintenance_status_breakdown = {}
    for status_choice in MaintenanceRecord.STATUS_CHOICES:
        status_code = status_choice[0]
        maintenance_status_breakdown[status_choice[1]] = (
            MaintenanceRecord.objects.filter(status=status_code).count()
        )

    # Maintenance by type category
    maintenance_type_breakdown = {}
    for type_choice in MaintenanceType.TYPE_CHOICES:
        type_code = type_choice[0]
        count = MaintenanceRecord.objects.filter(
            maintenance_type__type_category=type_code
        ).count()
        if count > 0:  # Only show categories with maintenance
            maintenance_type_breakdown[type_choice[1]] = count

    # Recent maintenance records
    recent_maintenance = MaintenanceRecord.objects.select_related(
        'aircraft', 'maintenance_type', 'performed_by'
    ).order_by('-created_at')[:5]

    # Overdue maintenance (detailed)
    overdue_maintenance_records = MaintenanceRecord.objects.filter(
        scheduled_date__lt=timezone.now().date(), status='scheduled'
    ).select_related('aircraft', 'maintenance_type')

    # Aircraft requiring maintenance
    aircraft_requiring_maintenance = (
        MaintenanceRecord.objects.filter(status__in=['scheduled', 'in_progress'])
        .values('aircraft__registration_mark')
        .distinct()
        .count()
    )

    # Maintenance efficiency metrics - calculate completion time differently
    completed_records = MaintenanceRecord.objects.filter(
        status='completed', started_date__isnull=False, completed_date__isnull=False
    )

    # Calculate average completion time in Python instead of SQL
    total_hours = 0
    count = 0
    for record in completed_records:
        if record.started_date and record.completed_date:
            delta = record.completed_date - record.started_date
            hours = delta.total_seconds() / 3600
            total_hours += hours
            count += 1

    avg_completion_time = round(total_hours / count, 2) if count > 0 else 0

    context = {
        'total_maintenance_records': total_maintenance_records,
        'active_maintenance': active_maintenance,
        'completed_maintenance': completed_maintenance,
        'overdue_maintenance': overdue_maintenance,
        'maintenance_status_breakdown': maintenance_status_breakdown,
        'maintenance_type_breakdown': maintenance_type_breakdown,
        'recent_maintenance': recent_maintenance,
        'overdue_maintenance_records': overdue_maintenance_records,
        'aircraft_requiring_maintenance': aircraft_requiring_maintenance,
        'avg_completion_time': (
            round(avg_completion_time, 1) if avg_completion_time else 0
        ),
    }
    return render(request, 'maintenance/dashboard.html', context)


# Maintenance Type CRUD Views
@login_required
def maintenance_type_list(request):
    """List all maintenance types with search and filtering"""
    maintenance_types = MaintenanceType.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        maintenance_types = maintenance_types.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(casa_reference__icontains=search_query)
        )

    # Filter by type category
    type_category = request.GET.get('type_category', '')
    if type_category:
        maintenance_types = maintenance_types.filter(type_category=type_category)

    # Filter by priority
    priority = request.GET.get('priority', '')
    if priority:
        maintenance_types = maintenance_types.filter(priority=priority)

    # Filter by certification required
    certification_required = request.GET.get('certification_required', '')
    if certification_required == 'true':
        maintenance_types = maintenance_types.filter(certification_required=True)
    elif certification_required == 'false':
        maintenance_types = maintenance_types.filter(certification_required=False)

    # Pagination
    paginator = Paginator(maintenance_types, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter choices for template
    type_category_choices = MaintenanceType.TYPE_CHOICES
    priority_choices = MaintenanceType.PRIORITY_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_category': type_category,
        'priority': priority,
        'certification_required': certification_required,
        'type_category_choices': type_category_choices,
        'priority_choices': priority_choices,
    }
    return render(request, 'maintenance/maintenance_type_list.html', context)


@login_required
def maintenance_type_detail(request, pk):
    """Display detailed view of maintenance type"""
    maintenance_type = get_object_or_404(MaintenanceType, pk=pk)

    # Get related maintenance records
    related_maintenance = (
        MaintenanceRecord.objects.filter(maintenance_type=maintenance_type)
        .select_related('aircraft', 'performed_by')
        .order_by('-scheduled_date')[:10]
    )

    context = {
        'maintenance_type': maintenance_type,
        'related_maintenance': related_maintenance,
    }
    return render(request, 'maintenance/maintenance_type_detail.html', context)


@login_required
def maintenance_type_create(request):
    """Create new maintenance type"""
    if request.method == 'POST':
        form = MaintenanceTypeForm(request.POST)
        if form.is_valid():
            maintenance_type = form.save()
            messages.success(
                request,
                f"Maintenance type '{maintenance_type.name}' created successfully.",
            )
            return redirect(
                'maintenance:maintenance_type_detail', pk=maintenance_type.pk
            )
    else:
        form = MaintenanceTypeForm()

    context = {
        'form': form,
        'title': 'Create Maintenance Type',
    }
    return render(request, 'maintenance/maintenance_type_form.html', context)


@login_required
def maintenance_type_update(request, pk):
    """Update existing maintenance type"""
    maintenance_type = get_object_or_404(MaintenanceType, pk=pk)

    if request.method == 'POST':
        form = MaintenanceTypeForm(request.POST, instance=maintenance_type)
        if form.is_valid():
            maintenance_type = form.save()
            messages.success(
                request,
                f"Maintenance type '{maintenance_type.name}' updated successfully.",
            )
            return redirect(
                'maintenance:maintenance_type_detail', pk=maintenance_type.pk
            )
    else:
        form = MaintenanceTypeForm(instance=maintenance_type)

    context = {
        'form': form,
        'maintenance_type': maintenance_type,
        'title': 'Update Maintenance Type',
    }
    return render(request, 'maintenance/maintenance_type_form.html', context)


@login_required
@require_http_methods(['DELETE'])
def maintenance_type_delete(request, pk):
    """Delete maintenance type (AJAX)"""
    maintenance_type = get_object_or_404(MaintenanceType, pk=pk)

    # Check if maintenance type has related records
    related_records = MaintenanceRecord.objects.filter(
        maintenance_type=maintenance_type
    ).count()
    if related_records > 0:
        return JsonResponse(
            {
                'success': False,
                'message': f"Cannot delete maintenance type '{maintenance_type.name}' with {related_records} related maintenance records.",
            },
            status=400,
        )

    try:
        name = maintenance_type.name
        maintenance_type.delete()
        return JsonResponse(
            {
                'success': True,
                'message': f"Maintenance type '{name}' deleted successfully.",
            }
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': f"Error deleting maintenance type: {str(e)}"},
            status=500,
        )


# Maintenance Record CRUD Views
@login_required
def maintenance_record_list(request):
    """List all maintenance records with search and filtering"""
    records = MaintenanceRecord.objects.select_related(
        'aircraft', 'maintenance_type', 'performed_by', 'supervised_by'
    )

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        records = records.filter(
            Q(maintenance_id__icontains=search_query)
            | Q(work_performed__icontains=search_query)
            | Q(aircraft__registration_mark__icontains=search_query)
            | Q(performed_by__user__first_name__icontains=search_query)
            | Q(performed_by__user__last_name__icontains=search_query)
        )

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        records = records.filter(status=status)

    # Filter by maintenance type category
    type_category = request.GET.get('type_category', '')
    if type_category:
        records = records.filter(maintenance_type__type_category=type_category)

    # Filter by aircraft
    aircraft_id = request.GET.get('aircraft', '')
    if aircraft_id:
        records = records.filter(aircraft_id=aircraft_id)

    # Filter by overdue
    overdue = request.GET.get('overdue', '')
    if overdue == 'true':
        records = records.filter(
            scheduled_date__lt=timezone.now().date(), status='scheduled'
        )

    # Date range filtering
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        records = records.filter(scheduled_date__gte=date_from)
    if date_to:
        records = records.filter(scheduled_date__lte=date_to)

    # Pagination
    paginator = Paginator(records, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter choices for template
    status_choices = MaintenanceRecord.STATUS_CHOICES
    type_category_choices = MaintenanceType.TYPE_CHOICES

    # Get aircraft choices for filter
    from aircraft.models import Aircraft

    aircraft_choices = Aircraft.objects.all().values('id', 'registration_mark')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'type_category': type_category,
        'aircraft_id': aircraft_id,
        'overdue': overdue,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': status_choices,
        'type_category_choices': type_category_choices,
        'aircraft_choices': aircraft_choices,
    }
    return render(request, 'maintenance/maintenance_record_list.html', context)


@login_required
def maintenance_record_detail(request, pk):
    """Display detailed view of maintenance record"""
    record = get_object_or_404(
        MaintenanceRecord.objects.select_related(
            'aircraft', 'maintenance_type', 'performed_by', 'supervised_by'
        ),
        pk=pk,
    )

    context = {
        'record': record,
    }
    return render(request, 'maintenance/maintenance_record_detail.html', context)


@login_required
def maintenance_record_create(request):
    """Create new maintenance record"""
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST, user=request.user)
        if form.is_valid():
            record = form.save()
            messages.success(
                request,
                f"Maintenance record '{record.maintenance_id}' created successfully.",
            )
            return redirect('maintenance:maintenance_record_detail', pk=record.pk)
    else:
        form = MaintenanceRecordForm(user=request.user)

    context = {
        'form': form,
        'title': 'Create Maintenance Record',
    }
    return render(request, 'maintenance/maintenance_record_form.html', context)


@login_required
def maintenance_record_update(request, pk):
    """Update existing maintenance record"""
    record = get_object_or_404(MaintenanceRecord, pk=pk)

    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST, instance=record, user=request.user)
        if form.is_valid():
            record = form.save()
            messages.success(
                request,
                f"Maintenance record '{record.maintenance_id}' updated successfully.",
            )
            return redirect('maintenance:maintenance_record_detail', pk=record.pk)
    else:
        form = MaintenanceRecordForm(instance=record, user=request.user)

    context = {
        'form': form,
        'record': record,
        'title': 'Update Maintenance Record',
    }
    return render(request, 'maintenance/maintenance_record_form.html', context)


@login_required
def maintenance_record_complete(request, pk):
    """Complete maintenance record"""
    record = get_object_or_404(MaintenanceRecord, pk=pk)

    if request.method == 'POST':
        form = MaintenanceCompletionForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            record.status = 'completed'
            record.save()
            messages.success(
                request,
                f"Maintenance record '{record.maintenance_id}' completed successfully.",
            )
            return redirect('maintenance:maintenance_record_detail', pk=record.pk)
    else:
        form = MaintenanceCompletionForm(instance=record)

    context = {
        'form': form,
        'record': record,
        'title': 'Complete Maintenance Record',
    }
    return render(request, 'maintenance/maintenance_completion_form.html', context)


@login_required
@require_http_methods(['DELETE'])
def maintenance_record_delete(request, pk):
    """Delete maintenance record (AJAX)"""
    record = get_object_or_404(MaintenanceRecord, pk=pk)

    # Check if record can be safely deleted (e.g., not if completed)
    if record.status == 'completed':
        return JsonResponse(
            {
                'success': False,
                'message': f"Cannot delete completed maintenance record '{record.maintenance_id}'.",
            },
            status=400,
        )

    try:
        maintenance_id = record.maintenance_id
        record.delete()
        return JsonResponse(
            {
                'success': True,
                'message': f"Maintenance record '{maintenance_id}' deleted successfully.",
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                'success': False,
                'message': f"Error deleting maintenance record: {str(e)}",
            },
            status=500,
        )


# Technical Log CRUD Views
@login_required
def technical_log_part_a_list(request):
    """List RPAS Technical Log Part A entries"""
    entries = RPASTechnicalLogPartA.objects.select_related(
        'aircraft', 'pilot_in_command'
    ).order_by('-flight_date')

    # Search and filtering
    search_query = request.GET.get('search', '')
    if search_query:
        entries = entries.filter(
            Q(aircraft__registration_mark__icontains=search_query)
            | Q(maintenance_schedule_reference__icontains=search_query)
            | Q(major_defects_notes__icontains=search_query)
        )

    aircraft_id = request.GET.get('aircraft', '')
    if aircraft_id:
        entries = entries.filter(aircraft_id=aircraft_id)

    # Pagination
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from aircraft.models import Aircraft

    aircraft_choices = Aircraft.objects.all().values('id', 'registration_mark')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'aircraft_id': aircraft_id,
        'aircraft_choices': aircraft_choices,
    }
    return render(request, 'maintenance/technical_log_part_a_list.html', context)


@login_required
def technical_log_part_a_create(request):
    """Create RPAS Technical Log Part A entry"""
    if request.method == 'POST':
        form = RPASTechnicalLogPartAForm(request.POST)
        if form.is_valid():
            entry = form.save()
            messages.success(
                request, "Technical Log Part A entry created successfully."
            )
            return redirect('maintenance:technical_log_part_a_list')
    else:
        form = RPASTechnicalLogPartAForm()

    context = {
        'form': form,
        'title': 'Create Technical Log Part A Entry',
    }
    return render(request, 'maintenance/technical_log_part_a_form.html', context)


@login_required
def technical_log_part_b_list(request):
    """List RPAS Technical Log Part B entries"""
    entries = RPASTechnicalLogPartB.objects.select_related(
        'aircraft', 'maintenance_type', 'performed_by'
    ).order_by('-maintenance_date')

    # Search and filtering
    search_query = request.GET.get('search', '')
    if search_query:
        entries = entries.filter(
            Q(aircraft__registration_mark__icontains=search_query)
            | Q(daily_inspection_certification__icontains=search_query)
        )

    aircraft_id = request.GET.get('aircraft', '')
    if aircraft_id:
        entries = entries.filter(aircraft_id=aircraft_id)

    # Pagination
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from aircraft.models import Aircraft

    aircraft_choices = Aircraft.objects.all().values('id', 'registration_mark')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'aircraft_id': aircraft_id,
        'aircraft_choices': aircraft_choices,
    }
    return render(request, 'maintenance/technical_log_part_b_list.html', context)


@login_required
def technical_log_part_b_create(request):
    """Create RPAS Technical Log Part B entry"""
    if request.method == 'POST':
        form = RPASTechnicalLogPartBForm(request.POST)
        if form.is_valid():
            entry = form.save()
            messages.success(
                request, "Technical Log Part B entry created successfully."
            )
            return redirect('maintenance:technical_log_part_b_list')
    else:
        form = RPASTechnicalLogPartBForm()

    context = {
        'form': form,
        'title': 'Create Technical Log Part B Entry',
    }
    return render(request, 'maintenance/technical_log_part_b_form.html', context)


# RPAS Maintenance Entry Views
@login_required
def rpas_maintenance_entry_list(request):
    """List RPAS Maintenance entries"""
    entries = RPASMaintenanceEntry.objects.select_related(
        'aircraft', 'performed_by'
    ).order_by('-entry_date')

    # Search and filtering
    search_query = request.GET.get('search', '')
    if search_query:
        entries = entries.filter(
            Q(technical_log_part_a__aircraft__registration_mark__icontains=search_query)
            | Q(item_description__icontains=search_query)
        )

    aircraft_id = request.GET.get('aircraft', '')
    if aircraft_id:
        entries = entries.filter(aircraft_id=aircraft_id)

    entry_type = request.GET.get('entry_type', '')
    if entry_type:
        entries = entries.filter(entry_type=entry_type)

    # Pagination
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from aircraft.models import Aircraft

    aircraft_choices = Aircraft.objects.all().values('id', 'registration_mark')
    entry_type_choices = []  # RPASMaintenanceEntry doesn't have ENTRY_TYPE_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'aircraft_id': aircraft_id,
        'entry_type': entry_type,
        'aircraft_choices': aircraft_choices,
        'entry_type_choices': entry_type_choices,
    }
    return render(request, 'maintenance/rpas_maintenance_entry_list.html', context)


@login_required
def rpas_maintenance_entry_create(request):
    """Create RPAS Maintenance entry"""
    if request.method == 'POST':
        form = RPASMaintenanceEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            messages.success(request, "RPAS Maintenance entry created successfully.")
            return redirect('maintenance:rpas_maintenance_entry_list')
    else:
        form = RPASMaintenanceEntryForm()

    context = {
        'form': form,
        'title': 'Create RPAS Maintenance Entry',
    }
    return render(request, 'maintenance/rpas_maintenance_entry_form.html', context)


# AJAX and Utility Views
@login_required
def get_maintenance_types_by_category(request):
    """Get maintenance types filtered by category (AJAX)"""
    category = request.GET.get('category')

    if not category:
        return JsonResponse({'maintenance_types': []})

    maintenance_types = MaintenanceType.objects.filter(type_category=category).values(
        'id', 'name', 'priority', 'estimated_duration_hours'
    )

    return JsonResponse({'maintenance_types': list(maintenance_types)})


@login_required
def ajax_maintenance_quick_info(request, pk):
    """Get quick maintenance information for AJAX requests"""
    try:
        record = MaintenanceRecord.objects.select_related(
            'aircraft', 'maintenance_type'
        ).get(pk=pk)

        data = {
            'success': True,
            'maintenance_id': record.maintenance_id,
            'maintenance_type': record.maintenance_type.name,
            'aircraft': record.aircraft.registration_mark,
            'status': record.get_status_display(),
            'scheduled_date': record.scheduled_date.strftime('%d/%m/%Y'),
            'performed_by': (
                record.performed_by.user.get_full_name()
                if record.performed_by
                else 'Not assigned'
            ),
        }
    except MaintenanceRecord.DoesNotExist:
        data = {'success': False, 'error': 'Maintenance record not found'}

    return JsonResponse(data)


# Export Views
@login_required
def maintenance_record_export(request, pk):
    """Export maintenance record as text (placeholder for PDF generation)"""
    from django.http import HttpResponse

    record = get_object_or_404(MaintenanceRecord, pk=pk)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        f'attachment; filename="{record.maintenance_id}_record.txt"'
    )

    content = f"""
MAINTENANCE RECORD EXPORT
=========================

Maintenance ID: {record.maintenance_id}
Aircraft: {record.aircraft.registration_mark}
Maintenance Type: {record.maintenance_type.name}
Category: {record.maintenance_type.get_type_category_display()}
Priority: {record.maintenance_type.get_priority_display()}

Performed By: {record.performed_by.user.get_full_name() if record.performed_by else 'Not assigned'}
Supervised By: {record.supervised_by.user.get_full_name() if record.supervised_by else 'N/A'}

Scheduled Date: {record.scheduled_date}
Started: {record.started_date or 'Not started'}
Completed: {record.completed_date or 'Not completed'}

Pre-Maintenance Hours: {record.pre_maintenance_hours}
Post-Maintenance Hours: {record.post_maintenance_hours or 'N/A'}

WORK DESCRIPTION:
{record.work_description}

DEFECTS FOUND:
{record.defects_found or 'None reported'}

CORRECTIVE ACTION:
{record.corrective_action or 'None required'}

PARTS USED:
{record.parts_used or 'None'}

STATUS: {record.get_status_display()}
COMPLETION STATUS: {record.get_completion_status_display() if record.completion_status else 'N/A'}

Return to Service: {'Yes' if record.return_to_service_authorized else 'No'}
Return to Service Date: {record.return_to_service_date or 'N/A'}

Created: {record.created_at}
Last Updated: {record.updated_at}
"""

    response.write(content)
    return response
