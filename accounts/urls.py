from django.urls import path

from . import crud_views, views

app_name = "accounts"

urlpatterns = [
    # Dashboard
    path("", crud_views.accounts_dashboard, name="dashboard"),
    # User CRUD
    path("users/", crud_views.user_list, name="user_list"),
    path("users/create/", crud_views.user_create, name="user_create"),
    path("users/<int:pk>/", crud_views.user_detail, name="user_detail"),
    path("users/<int:pk>/edit/", crud_views.user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", crud_views.user_delete, name="user_delete"),
    # Staff Profile CRUD
    path("staff/", crud_views.staff_list, name="staff_list"),
    path("staff/create/", crud_views.staff_create, name="staff_create"),
    path("staff/<int:pk>/", crud_views.staff_detail, name="staff_detail"),
    path("staff/<int:pk>/edit/", crud_views.staff_edit, name="staff_edit"),
    # Pilot Profile CRUD
    path("pilots/", crud_views.pilot_list, name="pilot_list"),
    path("pilots/create/", crud_views.pilot_create, name="pilot_create"),
    path("pilots/<int:pk>/", crud_views.pilot_detail, name="pilot_detail"),
    path("pilots/<int:pk>/edit/", crud_views.pilot_edit, name="pilot_edit"),
    # Client Profile CRUD
    path("clients/", crud_views.client_list, name="client_list"),
    path("clients/create/", crud_views.client_create, name="client_create"),
    path("clients/<int:pk>/", crud_views.client_detail, name="client_detail"),
    path("clients/<int:pk>/edit/", crud_views.client_edit, name="client_edit"),
    # Operator Certificate CRUD
    path("certificates/", crud_views.certificate_list, name="certificate_list"),
    path(
        "certificates/create/", crud_views.certificate_create, name="certificate_create"
    ),
    path(
        "certificates/<int:pk>/",
        crud_views.certificate_detail,
        name="certificate_detail",
    ),
    path(
        "certificates/<int:pk>/edit/",
        crud_views.certificate_edit,
        name="certificate_edit",
    ),
    # Key Personnel (Singleton)
    path("keypersonnel/", crud_views.keypersonnel_detail, name="keypersonnel_detail"),
    path("keypersonnel/edit/", crud_views.keypersonnel_edit, name="keypersonnel_edit"),
    # Authentication
    path("logout/", views.logout_view, name="logout"),
    path("login/", views.custom_login_view, name="login"),
    path("register/", views.register_view, name="register"),
]
