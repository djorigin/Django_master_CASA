from django.urls import path

from . import views

app_name = 'incidents'

urlpatterns = [
    # Dashboard
    path('', views.incidents_dashboard, name='dashboard'),
    # Incident Type URLs
    path('types/', views.incident_type_list, name='incident_type_list'),
    path('types/<int:pk>/', views.incident_type_detail, name='incident_type_detail'),
    path('types/create/', views.incident_type_create, name='incident_type_create'),
    path(
        'types/<int:pk>/update/',
        views.incident_type_update,
        name='incident_type_update',
    ),
    path(
        'types/<int:pk>/delete/',
        views.incident_type_delete,
        name='incident_type_delete',
    ),
    # Incident Report URLs
    path('reports/', views.incident_report_list, name='incident_report_list'),
    path(
        'reports/<int:pk>/', views.incident_report_detail, name='incident_report_detail'
    ),
    path(
        'reports/create/', views.incident_report_create, name='incident_report_create'
    ),
    path(
        'reports/<int:pk>/update/',
        views.incident_report_update,
        name='incident_report_update',
    ),
    path(
        'reports/<int:pk>/delete/',
        views.incident_report_delete,
        name='incident_report_delete',
    ),
    # Investigation and CASA Reporting URLs
    path(
        'reports/<int:pk>/investigation/',
        views.incident_investigation_update,
        name='incident_investigation_update',
    ),
    path(
        'reports/<int:pk>/casa-reporting/',
        views.casa_reporting_update,
        name='casa_reporting_update',
    ),
    # Export URLs
    path(
        'reports/<int:pk>/export/',
        views.incident_report_export,
        name='incident_report_export',
    ),
    # AJAX URLs
    path(
        'ajax/types-by-category/',
        views.get_incident_types_by_category,
        name='get_incident_types_by_category',
    ),
    path(
        'ajax/incident-quick-info/<int:pk>/',
        views.ajax_incident_quick_info,
        name='ajax_incident_quick_info',
    ),
]
