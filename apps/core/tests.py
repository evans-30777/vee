from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.packages.models import Package
from apps.services.models import Service

from .models import SiteSettings, Testimonial


class SiteSettingsTests(TestCase):
    def test_only_one_settings_record_allowed(self):
        SiteSettings.objects.create()
        with self.assertRaises(ValidationError):
            SiteSettings.objects.create()

    def test_whatsapp_url_built_from_number(self):
        settings_obj = SiteSettings.objects.create(whatsapp_number="254759643882")
        self.assertEqual(settings_obj.whatsapp_url, "https://wa.me/254759643882")

    def test_defaults_match_confirmed_business_facts(self):
        settings_obj = SiteSettings.objects.create()
        self.assertEqual(settings_obj.phone_calls, "0717115737")
        self.assertEqual(settings_obj.whatsapp_number, "254759643882")
        self.assertEqual(settings_obj.email, "hello@veeagency.co.ke")

    def test_load_returns_none_when_unconfigured(self):
        self.assertIsNone(SiteSettings.load())


class PublicPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create(service_counties=["Nairobi", "Machakos"])
        cls.service = Service.objects.create(
            name="SEO Optimization",
            slug="seo-optimization",
            short_description="Get found when people search.",
        )
        Package.objects.create(name="Essential Growth", slug="essential", price=15000)

    def test_key_pages_render(self):
        for url in [
            reverse("core:home"),
            reverse("core:about"),
            reverse("core:case_studies"),
            reverse("core:web_development"),
            reverse("services:list"),
            reverse("packages:list"),
            reverse("blog:list"),
            reverse("locations:list"),
            reverse("contact:contact"),
            reverse("core:privacy"),
            reverse("core:terms"),
            reverse("core:cookies"),
            reverse("core:disclaimer"),
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_pages_expose_canonical_and_meta(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(
            response.context["canonical_url"], "https://veeagency.co.ke/"
        )
        self.assertTrue(response.context["meta"]["title"])
        self.assertTrue(response.context["meta"]["description"])

    def test_inactive_service_is_not_publicly_reachable(self):
        self.service.is_active = False
        self.service.save()
        response = self.client.get(self.service.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_empty_testimonials_section_is_hidden(self):
        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, "What clients say")

    def test_testimonials_section_appears_when_records_exist(self):
        Testimonial.objects.create(client_name="A Client", quote="Real quote.")
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "What clients say")

    def test_blank_social_urls_render_no_links(self):
        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, ">Facebook<")
        self.assertNotContains(response, ">Instagram<")

    def test_sitemap_and_robots_are_served(self):
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, "/services/seo-optimization/")

        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertContains(robots, "Sitemap:")
        self.assertContains(robots, "Disallow: /admin/")
