from .models import SiteSettings


def site_settings(request):
    """Expose SiteSettings site-wide so templates never hard-code contact details."""
    return {"site_settings": SiteSettings.load()}
