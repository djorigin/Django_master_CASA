from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class CASAAdminSite(AdminSite):
    site_header = _('CASA Management System')
    site_title = _('CASA Admin')
    index_title = _('CASA Administration Dashboard')
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'title': self.index_title,
            'subtitle': _('Welcome to the CASA Aviation Management System'),
        })
        return super().index(request, extra_context)

# Create custom admin site instance
casa_admin_site = CASAAdminSite(name='casa_admin')