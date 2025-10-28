from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Import JSA model for register and detail views
from flight_operations.models import JobSafetyAssessment


def home(request):
    """
    Landing page with authentication flow logic:
    - If user is authenticated -> redirect to main system dashboard
    - If user is not authenticated -> show landing page with login CTA
    """
    if request.user.is_authenticated:
        return redirect(
            'core:main_system_dashboard'
        )  # Redirect to main system dashboard
    return render(request, "core/landing.html")


@login_required
def main_system_dashboard(request):
    """
    Main System Dashboard - Central hub for all aviation management modules
    This is the main dashboard users see after login, providing access to all system modules.
    """
    return render(request, "core/main_system_dashboard.html")


@login_required
def jsa_register(request):
    """
    Job Safety Assessment Register - Complete listing of all JSAs for CASA compliance.
    Provides site-wide access to JSA records outside of Flight Operations context.
    Critical for compliance management and audit trail review.
    """
    # Get all JSAs with related data for efficient queries
    jsas = JobSafetyAssessment.objects.select_related(
        'mission',
        'sop_reference',
        'related_aircraft_flight_plan',
        'related_drone_flight_plan',
        'related_flight_plan',
    ).order_by('-created_at')

    # Add creation context summary for each JSA
    jsa_list = []
    for jsa in jsas:
        context_details = jsa.get_creation_context_details()
        jsa_list.append(
            {
                'jsa': jsa,
                'context_summary': context_details['context_summary'],
                'approval_status': jsa.is_fully_approved,
            }
        )

    context = {
        'jsa_list': jsa_list,
        'total_jsas': len(jsa_list),
        'page_title': 'Job Safety Assessment Register',
        'page_description': 'Complete register of all Job Safety Assessments for CASA compliance and audit trail management',
    }

    return render(request, "core/jsa_register.html", context)


@login_required
def jsa_detail(request, jsa_id):
    """
    Job Safety Assessment Detail View with comprehensive audit trail.
    Shows complete JSA details, creation context, approval history, and review tracking.
    Essential for CASA compliance documentation and safety management system.
    """
    try:
        jsa = get_object_or_404(
            JobSafetyAssessment.objects.select_related(
                'mission',
                'sop_reference',
                'related_aircraft_flight_plan',
                'related_drone_flight_plan',
                'created_by',
            ),
            jsa_id=jsa_id,
        )
    except Http404:
        # Try to find by primary key if jsa_id format fails
        jsa = get_object_or_404(JobSafetyAssessment, pk=jsa_id)

    # Get comprehensive creation context
    creation_context = jsa.get_creation_context_details()

    # Prepare approval timeline for audit trail
    approval_timeline = []

    if jsa.crp_approval_signature and jsa.crp_approval_date:
        approval_timeline.append(
            {
                'type': 'CRP Approval',
                'signature': jsa.crp_approval_signature,
                'date': jsa.crp_approval_date,
                'description': 'Chief Remote Pilot / ARN Approval',
            }
        )

    if jsa.rp_approval_signature and jsa.rp_approval_date:
        approval_timeline.append(
            {
                'type': 'RP Approval',
                'signature': jsa.rp_approval_signature,
                'date': jsa.rp_approval_date,
                'description': 'Remote Pilot / ARN Approval',
            }
        )

    # Sort timeline by date
    approval_timeline.sort(
        key=lambda x: x['date'] if x['date'] else jsa.created_at.date()
    )

    context = {
        'jsa': jsa,
        'creation_context': creation_context,
        'approval_timeline': approval_timeline,
        'is_fully_approved': jsa.is_fully_approved,
        'page_title': f'JSA Detail: {jsa.jsa_id}',
        'page_description': f'Complete details and audit trail for Job Safety Assessment {jsa.jsa_id}',
    }

    return render(request, "core/jsa_detail.html", context)


@api_view(["GET"])
def client_greeting(request):
    return Response({"message": "Hello from Django API!"})


# Create your views here.
