from django.conf import settings
from django.templatetags.static import static

from .models import SiteSettings
from .seo import DEFAULT_SOCIAL_IMAGE, absolute_url, site_base_url


def site_settings(request):
    """Expose SiteSettings site-wide so templates never hard-code contact details."""
    current = SiteSettings.load()
    return {
        "site_settings": current,
        # Read by robots.txt and by the staging banner in base.html.
        "site_is_staging": settings.SITE_IS_STAGING,
        # Every page needs a sharing card, including 404 and anything rendered
        # without page_meta, so it is resolved here rather than per view.
        # Every schema block points at one business entity rather than each
        # page declaring its own unlinked copy.
        "organisation_id": f"{site_base_url()}/#organization",
        "default_social_image_url": (
            current.social_image_url if current else absolute_url(static(DEFAULT_SOCIAL_IMAGE))
        ),
    }
