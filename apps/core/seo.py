"""Page-level metadata contract shared by every public view."""

from django.conf import settings

# Applied site-wide so local relevance is not confined to the Locations app.
SERVICE_AREA_SUFFIX = "Nairobi, Machakos, Kajiado, Kiambu & across Kenya"

# Fallback sharing card, used when neither the page nor SiteSettings supplies one.
# Without it a shared link renders as a bare URL, which on WhatsApp — where most
# Kenyan referrals travel — looks broken.
DEFAULT_SOCIAL_IMAGE = "img/og-default.png"


def site_base_url():
    return settings.SITE_BASE_URL.rstrip("/")


def absolute_url(path):
    """Absolute URL for a path that may already be absolute.

    Open Graph and Twitter cards are fetched by servers with no page context,
    so a relative image path is simply dropped. Media URLs arrive relative.
    """
    if not path:
        return ""
    if path.startswith(("http://", "https://")):
        return path
    return f"{site_base_url()}/{path.lstrip('/')}"


def page_meta(request, *, title, description, page_class="", noindex=False, image=None):
    canonical_url = f"{site_base_url()}{request.path}"
    return {
        "meta": {
            "title": title,
            "description": description,
            "image": absolute_url(image) if image else "",
        },
        "canonical_url": canonical_url,
        "page_class": page_class,
        # A staging deployment is never indexable, whatever the view asked for.
        "noindex": noindex or settings.SITE_IS_STAGING,
    }


def breadcrumbs(*items):
    """Build a breadcrumb trail for both the visible list and its schema.

    Each item is (name, url_or_None). The last item is the current page and
    normally has no url. URLs are absolutised, because BreadcrumbList items
    are read without page context.
    """
    return [
        {"name": name, "url": absolute_url(url) if url else ""}
        for name, url in items
    ]
