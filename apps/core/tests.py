from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
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

    def test_click_to_call_number_is_normalised_to_international_format(self):
        """Owners may type any of these; the tel: link must stay dialable."""
        for entered in ["0717115737", "0717 115 737", "+254 717 115 737", "254717115737"]:
            with self.subTest(entered=entered):
                settings_obj = SiteSettings(phone_calls=entered)
                self.assertEqual(settings_obj.phone_calls_e164, "+254717115737")


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
        self.assertNotContains(response, "VEE Agency on Facebook")
        self.assertNotContains(response, "VEE Agency on Instagram")
        self.assertNotContains(response, "footer__social")

    def test_social_icon_appears_once_a_real_url_exists(self):
        settings_obj = SiteSettings.load()
        settings_obj.facebook_url = "https://facebook.com/veeagency"
        settings_obj.save()

        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "VEE Agency on Facebook")
        # Instagram is still blank, so its icon stays hidden.
        self.assertNotContains(response, "VEE Agency on Instagram")

    def test_click_to_call_link_uses_international_format(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'href="tel:+254717115737"')

    def test_stylesheet_and_script_are_linked(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "css/main.css")
        self.assertContains(response, "js/main.js")

    def test_prices_render_with_thousands_separators(self):
        response = self.client.get(reverse("packages:list"))
        self.assertContains(response, "15,000")
        self.assertNotContains(response, "KES&nbsp;15000")

    def test_skip_link_is_present_for_keyboard_users(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'class="skip-link" href="#main"')

    def test_first_hero_slide_is_active_without_javascript(self):
        """The carousel is progressive enhancement: slide one must render on its own."""
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'class="slide is-active"')

    def test_home_exposes_faq_schema_for_answer_engines(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "FAQPage")
        self.assertContains(response, "How much does a website cost in Kenya?")

    def test_mockups_are_labelled_as_examples_not_client_work(self):
        response = self.client.get(reverse("core:web_development"))
        self.assertContains(response, "not screenshots of client websites")

    def test_pages_carry_local_seo_language(self):
        for url in [reverse("core:home"), reverse("core:web_development"), reverse("services:list")]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "Nairobi")
                self.assertContains(response, "Kenya")

    def test_error_page_renders_standalone(self):
        """The 500 template must not depend on context processors or static files."""
        html = render_to_string("500.html")
        self.assertIn("Something went wrong", html)
        self.assertNotIn("{%", html)

    def test_sitemap_and_robots_are_served(self):
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, "/services/seo-optimization/")

        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertContains(robots, "Sitemap:")
        self.assertContains(robots, "Disallow: /admin/")
