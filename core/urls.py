from django.urls import path

from . import crud_views
from .views import (
    client_greeting,
    home,
    jsa_detail,
    jsa_register,
    main_system_dashboard,
)

app_name = "core"

urlpatterns = [
    path("", home, name="index"),  # Changed name from 'home' to 'index' for consistency
    path("api/greeting/", client_greeting),
    # Main System Dashboard - Central hub accessed after login
    path("dashboard/", main_system_dashboard, name="main_system_dashboard"),
    # Job Safety Assessment (JSA) Register and Detail Views - Site-wide access
    path("jsa/", jsa_register, name="jsa_register"),
    path("jsa/<str:jsa_id>/", jsa_detail, name="jsa_detail"),
    # Core Operations Management Dashboard - Specific to core module (SOPs, Training, Manuals)
    path(
        "core-operations/", crud_views.core_dashboard, name="core_operations_dashboard"
    ),
    # Standard Operating Procedures (SOP)
    path("sop/", crud_views.sop_list, name="sop_list"),
    path("sop/create/", crud_views.sop_create, name="sop_create"),
    path("sop/<int:pk>/", crud_views.sop_detail, name="sop_detail"),
    path("sop/<int:pk>/edit/", crud_views.sop_update, name="sop_update"),
    path("sop/<int:pk>/delete/", crud_views.sop_delete, name="sop_delete"),
    path("sop/<int:pk>/export/", crud_views.sop_export, name="sop_export"),
    path(
        "ajax/sop/quick-info/<int:pk>/",
        crud_views.ajax_sop_quick_info,
        name="ajax_sop_quick_info",
    ),
    # SOP Procedure Steps
    path("sop/<int:sop_pk>/steps/", crud_views.sop_steps_list, name="sop_steps_list"),
    path(
        "sop/<int:sop_pk>/steps/create/",
        crud_views.sop_step_create,
        name="sop_step_create",
    ),
    path(
        "sop/<int:sop_pk>/steps/<int:pk>/edit/",
        crud_views.sop_step_update,
        name="sop_step_update",
    ),
    path(
        "sop/<int:sop_pk>/steps/<int:pk>/delete/",
        crud_views.sop_step_delete,
        name="sop_step_delete",
    ),
    path(
        "ajax/sop-step/delete/<int:pk>/",
        crud_views.ajax_sop_step_delete,
        name="ajax_sop_step_delete",
    ),
    # Training Syllabus
    path("training/", crud_views.training_syllabus_list, name="training_syllabus_list"),
    path(
        "training/create/",
        crud_views.training_syllabus_create,
        name="training_syllabus_create",
    ),
    path(
        "training/<int:pk>/",
        crud_views.training_syllabus_detail,
        name="training_syllabus_detail",
    ),
    path(
        "training/<int:pk>/edit/",
        crud_views.training_syllabus_update,
        name="training_syllabus_update",
    ),
    path(
        "training/<int:pk>/delete/",
        crud_views.training_syllabus_delete,
        name="training_syllabus_delete",
    ),
    path(
        "training/<int:pk>/export/",
        crud_views.training_syllabus_export,
        name="training_syllabus_export",
    ),
    path(
        "ajax/training/quick-info/<int:pk>/",
        crud_views.ajax_training_syllabus_quick_info,
        name="ajax_training_syllabus_quick_info",
    ),
    # RPAS Operations Manual
    path(
        "operations-manual/",
        crud_views.operations_manual_list,
        name="operations_manual_list",
    ),
    path(
        "operations-manual/create/",
        crud_views.operations_manual_create,
        name="operations_manual_create",
    ),
    path(
        "operations-manual/<int:pk>/",
        crud_views.operations_manual_detail,
        name="operations_manual_detail",
    ),
    path(
        "operations-manual/<int:pk>/edit/",
        crud_views.operations_manual_update,
        name="operations_manual_update",
    ),
    path(
        "operations-manual/<int:pk>/delete/",
        crud_views.operations_manual_delete,
        name="operations_manual_delete",
    ),
    path(
        "operations-manual/<int:pk>/export/",
        crud_views.operations_manual_export,
        name="operations_manual_export",
    ),
    path(
        "ajax/operations-manual/quick-info/<int:pk>/",
        crud_views.ajax_operations_manual_quick_info,
        name="ajax_operations_manual_quick_info",
    ),
    # AJAX Delete Operations
    path(
        "ajax/sop/delete/<int:pk>/", crud_views.ajax_sop_delete, name="ajax_sop_delete"
    ),
    path(
        "ajax/training/delete/<int:pk>/",
        crud_views.ajax_training_syllabus_delete,
        name="ajax_training_syllabus_delete",
    ),
    path(
        "ajax/operations-manual/delete/<int:pk>/",
        crud_views.ajax_operations_manual_delete,
        name="ajax_operations_manual_delete",
    ),
    # Dashboard Statistics AJAX
    path(
        "ajax/dashboard-stats/",
        crud_views.ajax_dashboard_stats,
        name="ajax_dashboard_stats",
    ),
]
