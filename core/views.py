from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from rest_framework.decorators import api_view
from rest_framework.response import Response


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


@api_view(["GET"])
def client_greeting(request):
    return Response({"message": "Hello from Django API!"})


# Create your views here.
