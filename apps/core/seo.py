"""Page-level metadata contract shared by every public view."""

from django.conf import settings

# Applied site-wide so local relevance is not confined to the Locations app.
SERVICE_AREA_SUFFIX = "Nairobi, Machakos, Kajiado, Kiambu & across Kenya"


def page_meta(request, *, title, description, page_class="", noindex=False, image=None):
    canonical_url = f"{settings.SITE_BASE_URL.rstrip('/')}{request.path}"
    return {
        "meta": {"title": title, "description": description, "image": image},
        "canonical_url": canonical_url,
        "page_class": page_class,
        # A staging deployment is never indexable, whatever the view asked for.
        "noindex": noindex or settings.SITE_IS_STAGING,
    }
