from django.urls import path

from . import crud_views, views

app_name = "airspace"

urlpatterns = [
    # Dashboard
    path("", crud_views.airspace_dashboard, name="dashboard"),
    # Airspace Class URLs
    path("classes/", crud_views.airspace_class_list, name="airspace_class_list"),
    path(
        "classes/create/",
        crud_views.airspace_class_create,
        name="airspace_class_create",
    ),
    path(
        "classes/<int:pk>/",
        crud_views.airspace_class_detail,
        name="airspace_class_detail",
    ),
    path(
        "classes/<int:pk>/update/",
        crud_views.airspace_class_update,
        name="airspace_class_update",
    ),
    path(
        "classes/<int:pk>/delete/",
        crud_views.airspace_class_delete,
        name="airspace_class_delete",
    ),
    # Operational Area URLs
    path("areas/", crud_views.operational_area_list, name="operational_area_list"),
    path(
        "areas/create/",
        crud_views.operational_area_create,
        name="operational_area_create",
    ),
    path(
        "areas/<int:pk>/",
        crud_views.operational_area_detail,
        name="operational_area_detail",
    ),
    path(
        "areas/<int:pk>/update/",
        crud_views.operational_area_update,
        name="operational_area_update",
    ),
    path(
        "areas/<int:pk>/delete/",
        crud_views.operational_area_delete,
        name="operational_area_delete",
    ),
    # AJAX URLs
    path(
        "ajax/areas-by-class/",
        crud_views.get_operational_areas_by_class,
        name="get_operational_areas_by_class",
    ),
    path(
        "ajax/validate-area-id/",
        crud_views.validate_area_id,
        name="validate_area_id",
    ),
]
