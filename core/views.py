from django.shortcuts import redirect, render

from rest_framework.decorators import api_view
from rest_framework.response import Response


def home(request):
    """
    Landing page with authentication flow logic:
    - If user is authenticated -> redirect to company dashboard
    - If user is not authenticated -> show landing page with login CTA
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')  # Redirect to company dashboard
    return render(request, "core/landing.html")


@api_view(["GET"])
def client_greeting(request):
    return Response({"message": "Hello from Django API!"})


# Create your views here.
