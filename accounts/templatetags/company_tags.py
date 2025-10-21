"""
Template tags for company information.
"""

from django import template
from django.core.cache import cache

from accounts.models import CompanyContactDetails

register = template.Library()


@register.simple_tag
def company_name():
    """
    Get the company trading/display name with caching.
    Usage: {% company_name %}
    """
    cached_name = cache.get("company_display_name")
    if cached_name is None:
        try:
            company = CompanyContactDetails.get_instance()
            cached_name = company.display_name
        except Exception:
            cached_name = "CASA"  # Fallback

        # Cache for 1 hour
        cache.set("company_display_name", cached_name, 3600)

    return cached_name


@register.simple_tag
def company_legal_name():
    """
    Get the company legal name with caching.
    Usage: {% company_legal_name %}
    """
    cached_name = cache.get("company_legal_name")
    if cached_name is None:
        try:
            company = CompanyContactDetails.get_instance()
            cached_name = company.legal_entity_name
        except Exception:
            cached_name = "CASA"  # Fallback

        # Cache for 1 hour
        cache.set("company_legal_name", cached_name, 3600)

    return cached_name


@register.simple_tag
def company_arn():
    """
    Get the company ARN with caching.
    Usage: {% company_arn %}
    """
    cached_arn = cache.get("company_arn")
    if cached_arn is None:
        try:
            company = CompanyContactDetails.get_instance()
            cached_arn = company.arn
        except Exception:
            cached_arn = ""  # Fallback

        # Cache for 1 hour
        cache.set("company_arn", cached_arn, 3600)

    return cached_arn


@register.inclusion_tag("accounts/tags/company_info.html")
def company_info_block():
    """
    Render a complete company info block.
    Usage: {% company_info_block %}
    """
    company_data = cache.get("company_full_info")
    if company_data is None:
        try:
            company = CompanyContactDetails.get_instance()
            company_data = {
                "display_name": company.display_name,
                "legal_name": company.legal_entity_name,
                "trading_name": company.trading_name,
                "arn": company.arn,
                "abn": company.abn,
                "email": company.operational_hq_email,
                "phone": company.operational_hq_phone,
            }
        except Exception:
            company_data = {
                "display_name": "CASA",
                "legal_name": "CASA",
                "trading_name": "CASA",
                "arn": "",
                "abn": "",
                "email": "",
                "phone": "",
            }

        # Cache for 1 hour
        cache.set("company_full_info", company_data, 3600)

    return company_data


@register.filter
def replace_casa(value):
    """
    Replace 'CASA' in text with actual company name.
    Usage: {{ "Welcome to CASA"|replace_casa }}
    """
    if not value or "CASA" not in str(value):
        return value

    company_display_name = company_name()
    return str(value).replace("CASA", company_display_name)
