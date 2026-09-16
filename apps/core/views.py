from django.shortcuts import get_object_or_404, render

from apps.blog.models import BlogPost
from apps.locations.models import LocationPage
from apps.packages.models import Package
from apps.services.models import Service

from .models import CaseStudy, Testimonial
from .seo import page_meta

LEGAL_PAGES = {
    "privacy": "Privacy Policy",
    "terms": "Terms of Service",
    "cookies": "Cookie Policy",
    "disclaimer": "Disclaimer",
}


def home(request):
    context = {
        "services": Service.objects.filter(is_active=True)[:6],
        "packages": Package.objects.filter(
            is_active=True, billing_type=Package.BillingType.MONTHLY
        ),
        "website_package": Package.objects.filter(
            is_active=True, billing_type=Package.BillingType.ONE_TIME
        ).first(),
        # Empty-state rule: sections hide themselves when there is nothing real to show.
        "testimonials": Testimonial.objects.filter(is_active=True),
        "case_studies": CaseStudy.objects.filter(is_active=True)[:3],
        "recent_posts": BlogPost.published.all()[:3],
        **page_meta(
            request,
            title="VEE Agency — Digital Growth for Kenyan Businesses",
            description=(
                "VEE Agency helps businesses in Nairobi, Machakos, Kajiado, Kiambu "
                "and across Kenya get found and grow online through websites, SEO & AEO, "
                "Google Business Profile, social media and digital ads."
            ),
            page_class="home",
        ),
    }
    return render(request, "core/home.html", context)


def about(request):
    context = {
        "case_studies": CaseStudy.objects.filter(is_active=True),
        **page_meta(
            request,
            title="About VEE Agency — Digital Growth Partner in Kenya",
            description=(
                "VEE Agency is a digital growth partner based in Syokimau, Machakos County, "
                "working with businesses across Nairobi, Machakos, Kajiado, Kiambu and all of Kenya."
            ),
            page_class="about",
        ),
    }
    return render(request, "core/about.html", context)


def case_studies(request):
    context = {
        "case_studies": CaseStudy.objects.filter(is_active=True),
        **page_meta(
            request,
            title="Case Studies — VEE Agency",
            description=(
                "Real projects and results from VEE Agency's work with businesses "
                "in Nairobi, Machakos, Kajiado, Kiambu and across Kenya."
            ),
            page_class="case-studies",
        ),
    }
    return render(request, "core/case_studies.html", context)


def web_development(request):
    context = {
        "website_package": Package.objects.filter(
            is_active=True, billing_type=Package.BillingType.ONE_TIME
        ).first(),
        "location_pages": LocationPage.objects.filter(is_active=True),
        **page_meta(
            request,
            title="Website Design & Development in Kenya — VEE Agency",
            description=(
                "Custom website design and development from KES 30,000 — e-commerce, "
                "portfolio and booking websites built SEO, AEO and GEO ready for "
                "businesses in Nairobi, Machakos, Kajiado, Kiambu and across Kenya."
            ),
            page_class="web-development",
        ),
    }
    return render(request, "core/web_development.html", context)


def legal_page(request, doc):
    title = LEGAL_PAGES[doc]
    context = {
        "doc": doc,
        "doc_title": title,
        **page_meta(
            request,
            title=f"{title} — VEE Agency",
            description=f"{title} for VEE Agency, a digital growth agency based in Kenya.",
            page_class="legal",
        ),
    }
    return render(request, f"core/legal/{doc}.html", context)
