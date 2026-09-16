from django.shortcuts import get_object_or_404, render

from apps.core.seo import page_meta

from .models import LocationPage


def location_list(request):
    context = {
        "locations": LocationPage.objects.filter(is_active=True),
        **page_meta(
            request,
            title="Areas We Serve in Kenya — VEE Agency",
            description=(
                "VEE Agency works with businesses in Nairobi, Machakos, Kajiado and Kiambu, "
                "and serves clients across every county in Kenya remotely."
            ),
            page_class="locations",
        ),
    }
    return render(request, "locations/location_list.html", context)


def location_detail(request, slug):
    location = get_object_or_404(LocationPage, slug=slug, is_active=True)
    context = {
        "location": location,
        "featured_services": location.featured_services.filter(is_active=True),
        **page_meta(
            request,
            title=location.meta_title or f"Digital Marketing & Web Design in {location.county} — VEE Agency",
            description=location.meta_description or location.intro[:300],
            page_class="location-detail",
        ),
    }
    return render(request, "locations/location_detail.html", context)
