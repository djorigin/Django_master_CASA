from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import (
    CASAReportingForm,
    IncidentInvestigationForm,
    IncidentReportForm,
    IncidentTypeForm,
)
from .models import IncidentReport, IncidentType


@login_required
def incidents_dashboard(request):
    """Main incidents management dashboard with statistics"""
    # Basic statistics
    total_incidents = IncidentReport.objects.count()
    open_incidents = IncidentReport.objects.exclude(status='closed').count()
    casa_reportable = IncidentReport.objects.filter(
        incident_type__casa_reportable=True
    ).count()
    overdue_reports = IncidentReport.objects.filter(
        incident_type__casa_reportable=True, casa_reported=False
    ).count()

    # Incidents by status
    incident_status_breakdown = {}
    for status_choice in IncidentReport.STATUS_CHOICES:
        status_code = status_choice[0]
        incident_status_breakdown[status_choice[1]] = IncidentReport.objects.filter(
            status=status_code
        ).count()

    # Incidents by type category
    incident_category_breakdown = {}
    for category_choice in IncidentType.CATEGORY_CHOICES:
        category_code = category_choice[0]
        count = IncidentReport.objects.filter(
            incident_type__category=category_code
        ).count()
        if count > 0:  # Only show categories with incidents
            incident_category_breakdown[category_choice[1]] = count

    # Recent incidents
    recent_incidents = IncidentReport.objects.select_related(
        'incident_type', 'aircraft', 'pilot_in_command'
    ).order_by('-incident_date')[:5]

    # Overdue CASA reports (detailed)
    overdue_casa_reports = IncidentReport.objects.filter(
        incident_type__casa_reportable=True, casa_reported=False
    ).select_related('incident_type', 'aircraft')

    # Investigation status
    pending_investigations = IncidentReport.objects.filter(
        investigation_completed=False, status__in=['submitted', 'under_investigation']
    ).count()

    context = {
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
        'casa_reportable': casa_reportable,
        'overdue_reports': overdue_reports,
        'incident_status_breakdown': incident_status_breakdown,
        'incident_category_breakdown': incident_category_breakdown,
        'recent_incidents': recent_incidents,
        'overdue_casa_reports': overdue_casa_reports,
        'pending_investigations': pending_investigations,
    }
    return render(request, 'incidents/dashboard.html', context)


# Incident Type CRUD Views
@login_required
def incident_type_list(request):
    """List all incident types with search and filtering"""
    incident_types = IncidentType.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        incident_types = incident_types.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(casa_reference__icontains=search_query)
        )

    # Filter by category
    category = request.GET.get('category', '')
    if category:
        incident_types = incident_types.filter(category=category)

    # Filter by severity
    severity = request.GET.get('severity', '')
    if severity:
        incident_types = incident_types.filter(severity=severity)

    # Filter by CASA reportable
    casa_reportable = request.GET.get('casa_reportable', '')
    if casa_reportable == 'true':
        incident_types = incident_types.filter(casa_reportable=True)
    elif casa_reportable == 'false':
        incident_types = incident_types.filter(casa_reportable=False)

    # Pagination
    paginator = Paginator(incident_types, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter choices for template
    category_choices = IncidentType.CATEGORY_CHOICES
    severity_choices = IncidentType.SEVERITY_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category': category,
        'severity': severity,
        'casa_reportable': casa_reportable,
        'category_choices': category_choices,
        'severity_choices': severity_choices,
    }
    return render(request, 'incidents/incident_type_list.html', context)


@login_required
def incident_type_detail(request, pk):
    """Display detailed view of incident type"""
    incident_type = get_object_or_404(IncidentType, pk=pk)

    # Get related incidents
    related_incidents = (
        IncidentReport.objects.filter(incident_type=incident_type)
        .select_related('aircraft', 'pilot_in_command')
        .order_by('-incident_date')[:10]
    )

    context = {
        'incident_type': incident_type,
        'related_incidents': related_incidents,
    }
    return render(request, 'incidents/incident_type_detail.html', context)


@login_required
def incident_type_create(request):
    """Create new incident type"""
    if request.method == 'POST':
        form = IncidentTypeForm(request.POST)
        if form.is_valid():
            incident_type = form.save()
            messages.success(
                request, f"Incident type '{incident_type.name}' created successfully."
            )
            return redirect('incidents:incident_type_detail', pk=incident_type.pk)
    else:
        form = IncidentTypeForm()

    context = {
        'form': form,
        'title': 'Create Incident Type',
    }
    return render(request, 'incidents/incident_type_form.html', context)


@login_required
def incident_type_update(request, pk):
    """Update existing incident type"""
    incident_type = get_object_or_404(IncidentType, pk=pk)

    if request.method == 'POST':
        form = IncidentTypeForm(request.POST, instance=incident_type)
        if form.is_valid():
            incident_type = form.save()
            messages.success(
                request, f"Incident type '{incident_type.name}' updated successfully."
            )
            return redirect('incidents:incident_type_detail', pk=incident_type.pk)
    else:
        form = IncidentTypeForm(instance=incident_type)

    context = {
        'form': form,
        'incident_type': incident_type,
        'title': 'Update Incident Type',
    }
    return render(request, 'incidents/incident_type_form.html', context)


@login_required
@require_http_methods(['DELETE'])
def incident_type_delete(request, pk):
    """Delete incident type (AJAX)"""
    incident_type = get_object_or_404(IncidentType, pk=pk)

    # Check if incident type has related reports
    related_reports = IncidentReport.objects.filter(incident_type=incident_type).count()
    if related_reports > 0:
        return JsonResponse(
            {
                'success': False,
                'message': f"Cannot delete incident type '{incident_type.name}' with {related_reports} related incident reports.",
            },
            status=400,
        )

    try:
        name = incident_type.name
        incident_type.delete()
        return JsonResponse(
            {
                'success': True,
                'message': f"Incident type '{name}' deleted successfully.",
            }
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': f"Error deleting incident type: {str(e)}"},
            status=500,
        )


# Incident Report CRUD Views
@login_required
def incident_report_list(request):
    """List all incident reports with search and filtering"""
    reports = IncidentReport.objects.select_related(
        'incident_type', 'aircraft', 'pilot_in_command', 'reported_by'
    )

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        reports = reports.filter(
            Q(incident_id__icontains=search_query)
            | Q(summary__icontains=search_query)
            | Q(location_description__icontains=search_query)
            | Q(aircraft__registration__icontains=search_query)
            | Q(pilot_in_command__user__first_name__icontains=search_query)
            | Q(pilot_in_command__user__last_name__icontains=search_query)
        )

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        reports = reports.filter(status=status)

    # Filter by incident type category
    category = request.GET.get('category', '')
    if category:
        reports = reports.filter(incident_type__category=category)

    # Filter by CASA reportable
    casa_reportable = request.GET.get('casa_reportable', '')
    if casa_reportable == 'true':
        reports = reports.filter(incident_type__casa_reportable=True)
    elif casa_reportable == 'false':
        reports = reports.filter(incident_type__casa_reportable=False)

    # Filter by overdue CASA reports
    overdue_casa = request.GET.get('overdue_casa', '')
    if overdue_casa == 'true':
        reports = reports.filter(
            incident_type__casa_reportable=True, casa_reported=False
        )

    # Date range filtering
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        reports = reports.filter(incident_date__gte=date_from)
    if date_to:
        reports = reports.filter(incident_date__lte=date_to)

    # Pagination
    paginator = Paginator(reports, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter choices for template
    status_choices = IncidentReport.STATUS_CHOICES
    category_choices = IncidentType.CATEGORY_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'category': category,
        'casa_reportable': casa_reportable,
        'overdue_casa': overdue_casa,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': status_choices,
        'category_choices': category_choices,
    }
    return render(request, 'incidents/incident_report_list.html', context)


@login_required
def incident_report_detail(request, pk):
    """Display detailed view of incident report"""
    report = get_object_or_404(
        IncidentReport.objects.select_related(
            'incident_type', 'aircraft', 'pilot_in_command', 'reported_by'
        ),
        pk=pk,
    )

    context = {
        'report': report,
    }
    return render(request, 'incidents/incident_report_detail.html', context)


@login_required
def incident_report_create(request):
    """Create new incident report"""
    if request.method == 'POST':
        form = IncidentReportForm(request.POST, user=request.user)
        if form.is_valid():
            report = form.save()
            messages.success(
                request, f"Incident report '{report.incident_id}' created successfully."
            )
            return redirect('incidents:incident_report_detail', pk=report.pk)
    else:
        form = IncidentReportForm(user=request.user)

    context = {
        'form': form,
        'title': 'Create Incident Report',
    }
    return render(request, 'incidents/incident_report_form.html', context)


@login_required
def incident_report_update(request, pk):
    """Update existing incident report"""
    report = get_object_or_404(IncidentReport, pk=pk)

    if request.method == 'POST':
        form = IncidentReportForm(request.POST, instance=report, user=request.user)
        if form.is_valid():
            report = form.save()
            messages.success(
                request, f"Incident report '{report.incident_id}' updated successfully."
            )
            return redirect('incidents:incident_report_detail', pk=report.pk)
    else:
        form = IncidentReportForm(instance=report, user=request.user)

    context = {
        'form': form,
        'report': report,
        'title': 'Update Incident Report',
    }
    return render(request, 'incidents/incident_report_form.html', context)


@login_required
def incident_investigation_update(request, pk):
    """Update investigation details for incident report"""
    report = get_object_or_404(IncidentReport, pk=pk)

    if request.method == 'POST':
        form = IncidentInvestigationForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save()
            messages.success(
                request,
                f"Investigation details for '{report.incident_id}' updated successfully.",
            )
            return redirect('incidents:incident_report_detail', pk=report.pk)
    else:
        form = IncidentInvestigationForm(instance=report)

    context = {
        'form': form,
        'report': report,
        'title': 'Update Investigation Details',
    }
    return render(request, 'incidents/incident_investigation_form.html', context)


@login_required
def casa_reporting_update(request, pk):
    """Update CASA reporting details for incident report"""
    report = get_object_or_404(IncidentReport, pk=pk)

    if request.method == 'POST':
        form = CASAReportingForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save()
            messages.success(
                request,
                f"CASA reporting details for '{report.incident_id}' updated successfully.",
            )
            return redirect('incidents:incident_report_detail', pk=report.pk)
    else:
        form = CASAReportingForm(instance=report)

    context = {
        'form': form,
        'report': report,
        'title': 'Update CASA Reporting Details',
    }
    return render(request, 'incidents/casa_reporting_form.html', context)


@login_required
@require_http_methods(['DELETE'])
def incident_report_delete(request, pk):
    """Delete incident report (AJAX)"""
    report = get_object_or_404(IncidentReport, pk=pk)

    # Check if report can be safely deleted (e.g., not if CASA reported)
    if report.casa_reported:
        return JsonResponse(
            {
                'success': False,
                'message': f"Cannot delete incident report '{report.incident_id}' that has been reported to CASA.",
            },
            status=400,
        )

    try:
        incident_id = report.incident_id
        report.delete()
        return JsonResponse(
            {
                'success': True,
                'message': f"Incident report '{incident_id}' deleted successfully.",
            }
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': f"Error deleting incident report: {str(e)}"},
            status=500,
        )


# AJAX Views for dynamic functionality
@login_required
def get_incident_types_by_category(request):
    """Get incident types filtered by category (AJAX)"""
    category = request.GET.get('category')

    if not category:
        return JsonResponse({'incident_types': []})

    incident_types = IncidentType.objects.filter(category=category).values(
        'id', 'name', 'severity', 'casa_reportable'
    )

    return JsonResponse({'incident_types': list(incident_types)})


@login_required
def ajax_incident_quick_info(request, pk):
    """Get quick incident information for AJAX requests"""
    try:
        report = IncidentReport.objects.select_related('incident_type', 'aircraft').get(
            pk=pk
        )

        data = {
            'success': True,
            'incident_id': report.incident_id,
            'incident_type': report.incident_type.name,
            'aircraft': report.aircraft.registration if report.aircraft else 'N/A',
            'status': report.get_status_display(),
            'incident_date': report.incident_date.strftime('%d/%m/%Y %H:%M'),
            'location': report.location_description,
            'casa_reportable': report.incident_type.casa_reportable,
            'casa_reported': report.casa_reported,
        }
    except IncidentReport.DoesNotExist:
        data = {'success': False, 'error': 'Incident report not found'}

    return JsonResponse(data)


# Export and Reporting Views
@login_required
def incident_report_export(request, pk):
    """Export incident report as text (placeholder for PDF generation)"""
    from django.http import HttpResponse

    report = get_object_or_404(IncidentReport, pk=pk)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        f'attachment; filename="{report.incident_id}_report.txt"'
    )

    content = f"""
INCIDENT REPORT EXPORT
======================

Incident ID: {report.incident_id}
Incident Type: {report.incident_type.name} ({report.incident_type.get_severity_display()})
Aircraft: {report.aircraft.registration if report.aircraft else 'N/A'}
Pilot in Command: {report.pilot_in_command.user.get_full_name()}

Date/Time: {report.incident_date}
Location: {report.location_description}
Flight Phase: {report.get_flight_phase_display()}

SUMMARY:
{report.summary}

DETAILED DESCRIPTION:
{report.detailed_description}

CONTRIBUTING FACTORS:
{report.contributing_factors}

IMMEDIATE CAUSES:
{report.immediate_causes}

IMMEDIATE ACTIONS:
{report.immediate_actions}

CASA REPORTING:
CASA Reportable: {'Yes' if report.incident_type.casa_reportable else 'No'}
Reported to CASA: {'Yes' if report.casa_reported else 'No'}
CASA Report Date: {report.casa_report_date or 'Not reported'}
CASA Reference: {report.casa_reference_number or 'N/A'}

INVESTIGATION:
Completed: {'Yes' if report.investigation_completed else 'No'}
Completion Date: {report.investigation_completed_date or 'N/A'}
Findings: {report.investigation_findings or 'N/A'}

Report Created: {report.created_at}
Last Updated: {report.updated_at}
"""

    response.write(content)
    return response
