from django.urls import reverse
from django.shortcuts import get_object_or_404, render

from apps.core.seo import breadcrumbs, page_meta

from .models import Service


def service_list(request):
    context = {
        "services": Service.objects.filter(is_active=True),
        **page_meta(
            request,
            title="Digital Marketing & Web Services in Kenya — VEE Agency",
            description=(
                "SEO & AEO, Google Business Profile, social media, ads and competitor "
                "analysis for businesses across Kenya. Prices up front, free audit first."
            ),
            page_class="services",
        ),
    }
    return render(request, "services/service_list.html", context)


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    context = {
        "service": service,
        "related_services": Service.objects.filter(is_active=True).exclude(pk=service.pk)[:3],
        **page_meta(
            request,
            title=service.meta_title or f"{service.name} in Kenya — VEE Agency",
            description=service.meta_description or service.short_description[:300],
            page_class="service-detail",
        ),
        "breadcrumbs": breadcrumbs(
            ("Home", reverse("core:home")),
            ("Services", reverse("services:list")),
            (service.name, None),
        ),
    }
    return render(request, "services/service_detail.html", context)
