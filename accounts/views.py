from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CustomUserCreationForm
from .models import CustomUser


class CustomLoginForm(forms.Form):
    """Custom login form for aviation professionals"""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter your password'}
        )
    )


@login_required
def logout_view(request):
    """Logout view that redirects to dashboard"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("core:index")  # Redirect to home page


def custom_login_view(request):
    """
    Custom login view for aviation professionals:
    - Handles regular user authentication (not Django admin)
    - Works with basic, pilot, staff, and admin roles
    - Redirects to appropriate dashboard after login
    """
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Django expects username field, but we use email
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(
                    request, f'Welcome back, {user.get_full_name() or user.email}!'
                )
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """
    User registration view implementing enterprise business rules:
    - New users get 'basic' role by default (no privileges)
    - Only Admin/Staff can assign elevated permissions later
    - Redirects to login after successful registration
    """
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Let the form handle the complete save process including password hashing
            user = form.save()  # This handles password hashing correctly

            # Business rule is already handled in the form's save method

            messages.success(
                request,
                'Registration successful! Your account has been created with basic access. '
                'Contact an administrator to request additional permissions.',
            )

            # Redirect to login page after successful registration
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})
