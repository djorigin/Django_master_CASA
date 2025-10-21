from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import (
    ClientProfileForm,
    CustomUserForm,
    KeyPersonnelForm,
    OperatorCertificateForm,
    PilotProfileForm,
    StaffProfileForm,
)
from .models import (
    ClientProfile,
    CustomUser,
    KeyPersonnel,
    OperatorCertificate,
    PilotProfile,
    StaffProfile,
)


@login_required
def accounts_dashboard(request):
    """Main accounts dashboard with statistics"""
    # Get key personnel information
    personnel = KeyPersonnel.load()
    
    context = {
        "total_users": CustomUser.objects.count(),
        "active_staff": StaffProfile.objects.filter(is_active=True).count(),
        "available_pilots": PilotProfile.objects.filter(
            availability_status="available"
        ).count(),
        "active_clients": ClientProfile.objects.filter(status="active").count(),
        "active_certificates": OperatorCertificate.objects.filter(
            status="active"
        ).count(),
        "recent_users": CustomUser.objects.order_by("-date_joined")[:5],
        "key_personnel": personnel,
        "casa_compliance": personnel.is_casa_compliant(),
        "vacant_positions_count": len(personnel.get_vacant_positions()),
    }
    return render(request, "accounts/dashboard.html", context)


# CustomUser Views
@login_required
def user_list(request):
    """List all users with search and filtering"""
    users = CustomUser.objects.all().order_by("-date_joined")

    # Search functionality
    search_query = request.GET.get("search")
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    # Role filtering
    role_filter = request.GET.get("role")
    if role_filter:
        users = users.filter(role=role_filter)

    paginator = Paginator(users, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "role_filter": role_filter,
        "role_choices": CustomUser.ROLE_CHOICES,
    }
    return render(request, "accounts/user_list.html", context)


@login_required
def user_create(request):
    """Create new user"""
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, f"User {user.get_full_name()} created successfully."
            )
            return redirect("accounts:user_detail", pk=user.pk)
    else:
        form = CustomUserForm()

    context = {"form": form, "action": "Create"}
    return render(request, "accounts/user_form.html", context)


@login_required
def user_detail(request, pk):
    """User detail view"""
    user = get_object_or_404(CustomUser, pk=pk)
    context = {"user": user}
    return render(request, "accounts/user_detail.html", context)


@login_required
def user_edit(request, pk):
    """Edit user"""
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"User {user.get_full_name()} updated successfully."
            )
            return redirect("accounts:user_detail", pk=user.pk)
    else:
        form = CustomUserForm(instance=user)

    context = {"form": form, "user": user, "action": "Edit"}
    return render(request, "accounts/user_form.html", context)


@login_required
@require_http_methods(["POST"])
def user_delete(request, pk):
    """Delete user"""
    user = get_object_or_404(CustomUser, pk=pk)
    user_name = user.get_full_name()
    user.delete()
    messages.success(request, f"User {user_name} deleted successfully.")
    return redirect("accounts:user_list")


# Staff Profile Views
@login_required
def staff_list(request):
    """List all staff profiles"""
    staff = StaffProfile.objects.select_related("user").all()

    search_query = request.GET.get("search")
    if search_query:
        staff = staff.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(position_title__icontains=search_query)
            | Q(department__icontains=search_query)
        )

    department_filter = request.GET.get("department")
    if department_filter:
        staff = staff.filter(department=department_filter)

    paginator = Paginator(staff, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "department_filter": department_filter,
        "department_choices": StaffProfile.DEPARTMENT_CHOICES,
    }
    return render(request, "accounts/staff_list.html", context)


@login_required
def staff_create(request):
    """Create new staff profile"""
    if request.method == "POST":
        form = StaffProfileForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save()
            messages.success(
                request,
                f"Staff profile for {staff.user.get_full_name()} created successfully.",
            )
            return redirect("accounts:staff_detail", pk=staff.pk)
    else:
        form = StaffProfileForm()

    context = {"form": form, "action": "Create"}
    return render(request, "accounts/staff_form.html", context)


@login_required
def staff_detail(request, pk):
    """Staff profile detail view"""
    staff = get_object_or_404(StaffProfile.objects.select_related("user"), pk=pk)
    context = {"staff": staff}
    return render(request, "accounts/staff_detail.html", context)


@login_required
def staff_edit(request, pk):
    """Edit staff profile"""
    staff = get_object_or_404(StaffProfile, pk=pk)
    if request.method == "POST":
        form = StaffProfileForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Staff profile for {staff.user.get_full_name()} updated successfully.",
            )
            return redirect("accounts:staff_detail", pk=staff.pk)
    else:
        form = StaffProfileForm(instance=staff)

    context = {"form": form, "staff": staff, "action": "Edit"}
    return render(request, "accounts/staff_form.html", context)


# Pilot Profile Views
@login_required
def pilot_list(request):
    """List all pilot profiles"""
    pilots = PilotProfile.objects.select_related("user").all()

    search_query = request.GET.get("search")
    if search_query:
        pilots = pilots.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(arn__icontains=search_query)
            | Q(repl_number__icontains=search_query)
        )

    availability_filter = request.GET.get("availability")
    if availability_filter:
        pilots = pilots.filter(availability_status=availability_filter)

    paginator = Paginator(pilots, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "availability_filter": availability_filter,
        "availability_choices": PilotProfile.AVAILABILITY_CHOICES,
    }
    return render(request, "accounts/pilot_list.html", context)


@login_required
def pilot_create(request):
    """Create new pilot profile"""
    if request.method == "POST":
        form = PilotProfileForm(request.POST, request.FILES)
        if form.is_valid():
            pilot = form.save()
            messages.success(
                request,
                f"Pilot profile for {pilot.user.get_full_name()} created successfully.",
            )
            return redirect("accounts:pilot_detail", pk=pilot.pk)
    else:
        form = PilotProfileForm()

    context = {"form": form, "action": "Create"}
    return render(request, "accounts/pilot_form.html", context)


@login_required
def pilot_detail(request, pk):
    """Pilot profile detail view"""
    pilot = get_object_or_404(PilotProfile.objects.select_related("user"), pk=pk)
    context = {"pilot": pilot}
    return render(request, "accounts/pilot_detail.html", context)


@login_required
def pilot_edit(request, pk):
    """Edit pilot profile"""
    pilot = get_object_or_404(PilotProfile, pk=pk)
    if request.method == "POST":
        form = PilotProfileForm(request.POST, request.FILES, instance=pilot)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Pilot profile for {pilot.user.get_full_name()} updated successfully.",
            )
            return redirect("accounts:pilot_detail", pk=pilot.pk)
    else:
        form = PilotProfileForm(instance=pilot)

    context = {"form": form, "pilot": pilot, "action": "Edit"}
    return render(request, "accounts/pilot_form.html", context)


# Client Profile Views
@login_required
def client_list(request):
    """List all client profiles"""
    clients = ClientProfile.objects.select_related("user").all()

    search_query = request.GET.get("search")
    if search_query:
        clients = clients.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(company_name__icontains=search_query)
            | Q(abn__icontains=search_query)
        )

    status_filter = request.GET.get("status")
    if status_filter:
        clients = clients.filter(status=status_filter)

    paginator = Paginator(clients, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "status_filter": status_filter,
        "status_choices": ClientProfile.CLIENT_STATUS_CHOICES,
    }
    return render(request, "accounts/client_list.html", context)


@login_required
def client_create(request):
    """Create new client profile"""
    if request.method == "POST":
        form = ClientProfileForm(request.POST, request.FILES)
        if form.is_valid():
            client = form.save()
            messages.success(
                request,
                f"Client profile for {client.user.get_full_name()} created successfully.",
            )
            return redirect("accounts:client_detail", pk=client.pk)
    else:
        form = ClientProfileForm()

    context = {"form": form, "action": "Create"}
    return render(request, "accounts/client_form.html", context)


@login_required
def client_detail(request, pk):
    """Client profile detail view"""
    client = get_object_or_404(ClientProfile.objects.select_related("user"), pk=pk)
    context = {"client": client}
    return render(request, "accounts/client_detail.html", context)


@login_required
def client_edit(request, pk):
    """Edit client profile"""
    client = get_object_or_404(ClientProfile, pk=pk)
    if request.method == "POST":
        form = ClientProfileForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Client profile for {client.user.get_full_name()} updated successfully.",
            )
            return redirect("accounts:client_detail", pk=client.pk)
    else:
        form = ClientProfileForm(instance=client)

    context = {"form": form, "client": client, "action": "Edit"}
    return render(request, "accounts/client_form.html", context)


# Operator Certificate Views
@login_required
def certificate_list(request):
    """List all operator certificates"""
    certificates = OperatorCertificate.objects.all()

    search_query = request.GET.get("search")
    if search_query:
        certificates = certificates.filter(
            Q(reoc_number__icontains=search_query)
            | Q(company_name__icontains=search_query)
            | Q(casa_operator_number__icontains=search_query)
        )

    status_filter = request.GET.get("status")
    if status_filter:
        certificates = certificates.filter(status=status_filter)

    paginator = Paginator(certificates, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "status_filter": status_filter,
        "status_choices": OperatorCertificate.STATUS_CHOICES,
    }
    return render(request, "accounts/certificate_list.html", context)


@login_required
def certificate_create(request):
    """Create new operator certificate"""
    if request.method == "POST":
        form = OperatorCertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save()
            messages.success(
                request,
                f"Operator certificate {certificate.reoc_number} created successfully.",
            )
            return redirect("accounts:certificate_detail", pk=certificate.pk)
    else:
        form = OperatorCertificateForm()

    context = {"form": form, "action": "Create"}
    return render(request, "accounts/certificate_form.html", context)


@login_required
def certificate_detail(request, pk):
    """Operator certificate detail view"""
    certificate = get_object_or_404(OperatorCertificate, pk=pk)
    context = {"certificate": certificate}
    return render(request, "accounts/certificate_detail.html", context)


@login_required
def certificate_edit(request, pk):
    """Edit operator certificate"""
    certificate = get_object_or_404(OperatorCertificate, pk=pk)
    if request.method == "POST":
        form = OperatorCertificateForm(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Operator certificate {certificate.reoc_number} updated successfully.",
            )
            return redirect("accounts:certificate_detail", pk=certificate.pk)
    else:
        form = OperatorCertificateForm(instance=certificate)

    context = {"form": form, "certificate": certificate, "action": "Edit"}
    return render(request, "accounts/certificate_form.html", context)


# KeyPersonnel Views (Singleton Pattern)
@login_required
def keypersonnel_detail(request):
    """Display key personnel information - CASA required positions"""
    personnel = KeyPersonnel.load()  # Load singleton instance
    context = {
        "personnel": personnel,
        "personnel_summary": personnel.get_personnel_summary(),
        "vacant_positions": personnel.get_vacant_positions(),
        "is_casa_compliant": personnel.is_casa_compliant(),
    }
    return render(request, "accounts/keypersonnel_detail.html", context)


@login_required
def keypersonnel_edit(request):
    """Edit key personnel information - singleton pattern"""
    personnel = KeyPersonnel.load()  # Load or create singleton instance
    
    if request.method == "POST":
        form = KeyPersonnelForm(request.POST, instance=personnel)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Key Personnel information updated successfully."
            )
            return redirect("accounts:keypersonnel_detail")
    else:
        form = KeyPersonnelForm(instance=personnel)

    context = {
        "form": form,
        "personnel": personnel,
        "action": "Edit",
        "vacant_positions": personnel.get_vacant_positions(),
    }
    return render(request, "accounts/keypersonnel_form.html", context)
