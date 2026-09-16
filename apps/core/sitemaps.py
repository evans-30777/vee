from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import BlogPost, Category
from apps.locations.models import LocationPage
from apps.services.models import Service


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return [
            "core:home",
            "core:about",
            "core:case_studies",
            "core:web_development",
            "services:list",
            "packages:list",
            "blog:list",
            "locations:list",
            "contact:contact",
            "core:privacy",
            "core:terms",
            "core:cookies",
            "core:disclaimer",
        ]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class LocationSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return LocationPage.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.published.all()

    def lastmod(self, obj):
        return obj.updated_at


class BlogCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "locations": LocationSitemap,
    "posts": BlogPostSitemap,
    "categories": BlogCategorySitemap,
}
