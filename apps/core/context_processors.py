from django.conf import settings

from .models import SiteSettings


def site_settings(request):
    """Expose SiteSettings site-wide so templates never hard-code contact details."""
    return {
        "site_settings": SiteSettings.load(),
        # Read by robots.txt and by the staging banner in base.html.
        "site_is_staging": settings.SITE_IS_STAGING,
    }
