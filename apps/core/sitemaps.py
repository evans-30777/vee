from urllib.parse import urlsplit

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.core.seo import site_base_url

from apps.blog.models import BlogPost, Category
from apps.core.models import CaseStudy
from apps.locations.models import LocationPage
from apps.services.models import Service


# Priority is relative within this site only. The home page is the entry point,
# the commercial pages rank below it, and the legal pages are listed so they can
# be found but are never what we want surfaced.
STATIC_PAGE_PRIORITY = {
    "core:home": 1.0,
    "services:list": 0.9,
    "packages:list": 0.9,
    "core:web_development": 0.9,
    "locations:list": 0.7,
    "blog:list": 0.7,
    "core:about": 0.6,
    "contact:contact": 0.6,
    "core:privacy": 0.2,
    "core:terms": 0.2,
    "core:cookies": 0.2,
    "core:disclaimer": 0.2,
}


class CanonicalSitemap(Sitemap):
    """Emits the same host the canonical tags use.

    Canonicals come from SITE_BASE_URL while the sitemap defaulted to the
    request's host. The day those disagree — www versus bare, or a stale env
    var after the move to HostAfrica — the sitemap lists URLs whose canonical
    points somewhere else, which is a conflicting signal and very hard to spot.
    """

    def get_protocol(self, protocol=None):
        return urlsplit(site_base_url()).scheme or "https"

    def get_domain(self, site=None):
        return urlsplit(site_base_url()).netloc


class StaticViewSitemap(CanonicalSitemap):
    changefreq = "monthly"

    def lastmod(self, item):
        """Newest content change, so a crawler can tell whether to bother.

        These pages have no row of their own, so the best available signal is
        the most recent edit to anything they display.
        """
        stamps = [
            Service.objects.order_by("-updated_at").values_list("updated_at", flat=True).first(),
            LocationPage.objects.order_by("-updated_at").values_list("updated_at", flat=True).first(),
            BlogPost.published.order_by("-updated_at").values_list("updated_at", flat=True).first(),
        ]
        stamps = [stamp for stamp in stamps if stamp]
        return max(stamps) if stamps else None

    def items(self):
        pages = list(STATIC_PAGE_PRIORITY)
        # Case studies are only worth submitting once there is one to show.
        # An empty page is thin content, and thin content on a new domain is
        # exactly the signal the site cannot afford.
        if CaseStudy.objects.filter(is_active=True).exists():
            pages.append("core:case_studies")
        return pages

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return STATIC_PAGE_PRIORITY.get(item, 0.5)


class ServiceSitemap(CanonicalSitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class LocationSitemap(CanonicalSitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return LocationPage.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class BlogPostSitemap(CanonicalSitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.published.all()

    def lastmod(self, obj):
        return obj.updated_at


class BlogCategorySitemap(CanonicalSitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        # Only categories that actually have something in them. An empty
        # category page is a dead end for a reader and a thin page for Google.
        return Category.objects.filter(is_active=True, posts__in=BlogPost.published.all()).distinct()

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "locations": LocationSitemap,
    "posts": BlogPostSitemap,
    "categories": BlogCategorySitemap,
}
