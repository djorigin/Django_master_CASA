from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def logout_view(request):
    """Logout view that redirects to dashboard"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("core:index")  # Redirect to home page


def custom_login_view(request):
    """Redirect to admin login but return to accounts dashboard"""
    from django.contrib.admin.views.decorators import staff_member_required
    from django.urls import reverse

    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    # Otherwise redirect to admin login with next parameter
    admin_login_url = "/admin/login/?next=" + reverse("accounts:dashboard")
    return redirect(admin_login_url)
