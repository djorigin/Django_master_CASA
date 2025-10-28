from django.urls import path

from . import views

app_name = 'maintenance'

urlpatterns = [
    # Dashboard
    path('', views.maintenance_dashboard, name='dashboard'),
    # Maintenance Type URLs
    path('types/', views.maintenance_type_list, name='maintenance_type_list'),
    path(
        'types/<int:pk>/', views.maintenance_type_detail, name='maintenance_type_detail'
    ),
    path(
        'types/create/', views.maintenance_type_create, name='maintenance_type_create'
    ),
    path(
        'types/<int:pk>/update/',
        views.maintenance_type_update,
        name='maintenance_type_update',
    ),
    path(
        'types/<int:pk>/delete/',
        views.maintenance_type_delete,
        name='maintenance_type_delete',
    ),
    # Maintenance Record URLs
    path('records/', views.maintenance_record_list, name='maintenance_record_list'),
    path(
        'records/<int:pk>/',
        views.maintenance_record_detail,
        name='maintenance_record_detail',
    ),
    path(
        'records/create/',
        views.maintenance_record_create,
        name='maintenance_record_create',
    ),
    path(
        'records/<int:pk>/update/',
        views.maintenance_record_update,
        name='maintenance_record_update',
    ),
    path(
        'records/<int:pk>/complete/',
        views.maintenance_record_complete,
        name='maintenance_record_complete',
    ),
    path(
        'records/<int:pk>/delete/',
        views.maintenance_record_delete,
        name='maintenance_record_delete',
    ),
    # Technical Log URLs
    path(
        'technical-log/part-a/',
        views.technical_log_part_a_list,
        name='technical_log_part_a_list',
    ),
    path(
        'technical-log/part-a/create/',
        views.technical_log_part_a_create,
        name='technical_log_part_a_create',
    ),
    path(
        'technical-log/part-b/',
        views.technical_log_part_b_list,
        name='technical_log_part_b_list',
    ),
    path(
        'technical-log/part-b/create/',
        views.technical_log_part_b_create,
        name='technical_log_part_b_create',
    ),
    # RPAS Maintenance Entry URLs
    path(
        'rpas-entries/',
        views.rpas_maintenance_entry_list,
        name='rpas_maintenance_entry_list',
    ),
    path(
        'rpas-entries/create/',
        views.rpas_maintenance_entry_create,
        name='rpas_maintenance_entry_create',
    ),
    # Export URLs
    path(
        'records/<int:pk>/export/',
        views.maintenance_record_export,
        name='maintenance_record_export',
    ),
    # AJAX URLs
    path(
        'ajax/types-by-category/',
        views.get_maintenance_types_by_category,
        name='get_maintenance_types_by_category',
    ),
    path(
        'ajax/maintenance-quick-info/<int:pk>/',
        views.ajax_maintenance_quick_info,
        name='ajax_maintenance_quick_info',
    ),
]
