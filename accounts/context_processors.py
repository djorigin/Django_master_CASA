"""
Context processors for making data available to all templates.
"""

from django.core.cache import cache

from accounts.models import CompanyContactDetails


def company_details(request):
    """
    Add company details to all template contexts.
    Uses caching to minimize database hits.
    """
    # Try to get from cache first (1 hour cache)
    company_data = cache.get("company_details")

    if company_data is None:
        try:
            company = CompanyContactDetails.get_instance()
            company_data = {
                "legal_name": company.legal_entity_name,
                "trading_name": company.trading_name,
                "display_name": company.display_name,
                "arn": company.arn,
                "abn": company.abn,
                "operational_email": company.operational_hq_email,
                "operational_phone": company.operational_hq_phone,
            }
            # Cache for 1 hour (3600 seconds)
            cache.set("company_details", company_data, 3600)
        except Exception:
            # Fallback if no company details exist
            company_data = {
                "legal_name": "CASA",
                "trading_name": "CASA",
                "display_name": "CASA",
                "arn": "",
                "abn": "",
                "operational_email": "",
                "operational_phone": "",
            }

    return {"company": company_data}
