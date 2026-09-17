from datetime import date

from django.urls import reverse
from django.shortcuts import get_object_or_404, render

from apps.blog.models import BlogPost
from apps.locations.models import LocationPage
from apps.packages.models import Package
from apps.services.models import Service

from .models import CaseStudy, Testimonial
from .seo import breadcrumbs, page_meta

# Title and the date each document was last substantively revised.
#
# The date is recorded here rather than rendered from `now`, which would make
# every legal page claim to have been updated today, on every page load. The
# Privacy Policy tells the reader this date shows when the document last
# changed, so it has to be true. Update the date when you change the wording.
LEGAL_PAGES = {
    "privacy": ("Privacy Policy", date(2026, 9, 17)),
    "terms": ("Terms of Service", date(2026, 9, 17)),
    "cookies": ("Cookie Policy", date(2026, 9, 17)),
    "disclaimer": ("Disclaimer", date(2026, 9, 17)),
}


def home(request):
    context = {
        # All of them. The slice hid Digital Ads Management — a service the
        # Growth System section on this same page argues for by name.
        "services": Service.objects.filter(is_active=True),
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
                "Websites, SEO & AEO, Google Business Profile and ads for businesses "
                "in Nairobi, Machakos, Kajiado, Kiambu and across Kenya. Free audit first."
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
    published = CaseStudy.objects.filter(is_active=True)
    context = {
        "case_studies": published,
        **page_meta(
            request,
            title="Case Studies — VEE Agency",
            description=(
                "Real projects and results from VEE Agency's work with businesses "
                "in Nairobi, Machakos, Kajiado, Kiambu and across Kenya."
            ),
            page_class="case-studies",
            # Nothing to show yet means nothing worth indexing. The page stays
            # reachable, but it is not offered to search as thin content.
            noindex=not published.exists(),
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
                "Websites from KES 30,000 for Kenyan businesses — e-commerce, portfolio "
                "and booking sites, built mobile-first and search-ready. Free audit first."
            ),
            page_class="web-development",
        ),
        "breadcrumbs": breadcrumbs(
            ("Home", reverse("core:home")),
            ("Web Development", None),
        ),
    }
    return render(request, "core/web_development.html", context)


def legal_page(request, doc):
    title, updated_at = LEGAL_PAGES[doc]
    context = {
        "doc": doc,
        "doc_title": title,
        "doc_updated_at": updated_at,
        **page_meta(
            request,
            title=f"{title} — VEE Agency",
            description=f"{title} for VEE Agency, a digital growth agency based in Kenya.",
            page_class="legal",
        ),
        "breadcrumbs": breadcrumbs(
            ("Home", reverse("core:home")),
            (title, None),
        ),
    }
    return render(request, f"core/legal/{doc}.html", context)
