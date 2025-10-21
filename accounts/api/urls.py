from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    CustomUserViewSet,
    StaffProfileViewSet,
    PilotProfileViewSet,
    ClientProfileViewSet,
    OperatorCertificateViewSet,
    CompanyContactDetailsViewSet,
    KeyPersonnelViewSet,
)

# Create router and register viewsets
router = DefaultRouter()

# Register all viewsets with the router
router.register(r"users", CustomUserViewSet, basename="user")
router.register(r"staff", StaffProfileViewSet, basename="staff")
router.register(r"pilots", PilotProfileViewSet, basename="pilot")
router.register(r"clients", ClientProfileViewSet, basename="client")
router.register(r"certificates", OperatorCertificateViewSet, basename="certificate")
router.register(r"company", CompanyContactDetailsViewSet, basename="company")
router.register(r"key-personnel", KeyPersonnelViewSet, basename="keypersonnel")

# API URL patterns
app_name = "accounts_api"

urlpatterns = [
    # Include all router URLs
    path("", include(router.urls)),
]
