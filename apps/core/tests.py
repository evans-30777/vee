import html
import json
import re

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User
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


class StagingModeTests(TestCase):
    """A public test copy must never be indexable.

    Left crawlable it competes with the live site as duplicate content, which is
    expensive to undo once Google has indexed it.
    """

    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()

    @override_settings(SITE_IS_STAGING=True)
    def test_every_page_sends_noindex_in_staging(self):
        for url in [
            reverse("core:home"),
            reverse("core:about"),
            reverse("core:web_development"),
            reverse("packages:list"),
            reverse("contact:contact"),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTrue(response.context["noindex"])
                self.assertContains(response, "noindex")

    @override_settings(SITE_IS_STAGING=True)
    def test_robots_disallows_everything_in_staging(self):
        response = self.client.get("/robots.txt")
        self.assertContains(response, "Disallow: /")
        # The sitemap must not be advertised, or crawlers are invited in anyway.
        self.assertNotContains(response, "Sitemap:")

    @override_settings(SITE_IS_STAGING=True)
    def test_staging_banner_is_shown(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "staging-flag")
        self.assertContains(response, "not the live site")

    def test_production_is_indexable_and_unbannered(self):
        """The guard must not leak into the real site."""
        response = self.client.get(reverse("core:home"))
        self.assertFalse(response.context["noindex"])
        self.assertNotContains(response, "staging-flag")

        robots = self.client.get("/robots.txt")
        self.assertContains(robots, "Allow: /")
        self.assertContains(robots, "Sitemap:")


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

    def test_no_cookie_banner_when_nothing_sets_optional_cookies(self):
        """Asking consent for cookies the site does not set would be untrue."""
        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, "data-cookie-banner")
        self.assertNotContains(response, "Cookie settings")

    def test_cookie_banner_appears_once_analytics_is_configured(self):
        settings_obj = SiteSettings.load()
        settings_obj.ga4_measurement_id = "G-TEST12345"
        settings_obj.save()

        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "data-cookie-banner")
        self.assertContains(response, "data-cookie-settings")

    def test_tracking_scripts_are_absent_until_consent_is_given(self):
        """The whole point of the banner: no third-party script ships with the page."""
        settings_obj = SiteSettings.load()
        settings_obj.ga4_measurement_id = "G-TEST12345"
        settings_obj.meta_pixel_id = "111222333"
        settings_obj.save()

        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, "googletagmanager.com")
        self.assertNotContains(response, "connect.facebook.net")
        self.assertNotContains(response, "fbevents.js")

    def test_decline_is_offered_as_prominently_as_accept(self):
        settings_obj = SiteSettings.load()
        settings_obj.ga4_measurement_id = "G-TEST12345"
        settings_obj.save()

        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "data-cookie-decline")
        self.assertContains(response, "data-cookie-accept")

    def test_search_console_tag_renders_without_consent(self):
        """It sets no cookie, so it must not be gated behind the banner."""
        settings_obj = SiteSettings.load()
        settings_obj.google_site_verification = "verify-token-abc"
        settings_obj.save()

        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'name="google-site-verification"')
        self.assertContains(response, "verify-token-abc")
        self.assertNotContains(response, "data-cookie-banner")

    def test_sets_optional_cookies_property(self):
        settings_obj = SiteSettings.load()
        self.assertFalse(settings_obj.sets_optional_cookies)

        settings_obj.meta_pixel_id = "111222333"
        settings_obj.save()
        self.assertTrue(settings_obj.sets_optional_cookies)

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


class StructuredDataTests(TestCase):
    """Schema and metadata are easy to break silently and never notice.

    Every one of these was a real finding: descriptions running past Google's
    cut, a business entity declared separately on each page with no @id, and
    breadcrumb trails rendered as decoration with no markup behind them.
    """

    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()
        # The seeder needs an author or it skips the posts entirely, which
        # would quietly turn the blog assertions below into 404 checks.
        User.objects.create_superuser(
            username="evans", email="hello@veeagency.co.ke", password="x",
            first_name="Evans",
        )
        call_command("seed_content", "--with-posts", verbosity=0)

    def _pages(self):
        return [
            reverse("core:home"),
            reverse("core:about"),
            reverse("core:web_development"),
            reverse("services:list"),
            reverse("packages:list"),
            reverse("blog:list"),
            reverse("locations:list"),
            reverse("contact:contact"),
            reverse("core:privacy"),
            "/services/seo-optimization/",
            "/locations/nairobi/",
            "/blog/website-cost-kenya/",
        ]

    def test_every_json_ld_block_parses(self):
        for path in self._pages():
            body = self.client.get(path).content.decode()
            blocks = re.findall(
                r'<script type="application/ld\+json">(.*?)</script>', body, re.S
            )
            self.assertTrue(blocks, f"{path} has no structured data")
            for block in blocks:
                try:
                    json.loads(block)
                except json.JSONDecodeError as error:
                    self.fail(f"{path}: invalid JSON-LD — {error}")

    def test_no_page_declares_the_business_twice(self):
        """Each page declaring its own unlinked copy fragments the entity."""
        for path in self._pages():
            body = self.client.get(path).content.decode()
            types = [
                json.loads(block).get("@type")
                for block in re.findall(
                    r'<script type="application/ld\+json">(.*?)</script>', body, re.S
                )
            ]
            self.assertLessEqual(
                types.count("ProfessionalService"), 1,
                f"{path} declares the business more than once",
            )

    def test_the_business_entity_carries_a_stable_id(self):
        body = self.client.get(reverse("core:home")).content.decode()
        self.assertIn("#organization", body)

    def test_meta_descriptions_fit_in_a_search_result(self):
        """Past ~160 characters Google truncates, losing the reason to click."""
        for path in self._pages():
            body = self.client.get(path).content.decode()
            match = re.search(r'<meta name="description" content="(.*?)"', body, re.S)
            self.assertIsNotNone(match, f"{path} has no description")
            description = html.unescape(match.group(1))
            self.assertLessEqual(
                len(description), 160,
                f"{path}: description is {len(description)} characters",
            )
            self.assertGreater(len(description), 50, f"{path}: description is too thin")

    def test_titles_fit_in_a_search_result(self):
        for path in self._pages():
            body = self.client.get(path).content.decode()
            title = html.unescape(re.search(r"<title>(.*?)</title>", body, re.S).group(1))
            self.assertLessEqual(len(title), 60, f"{path}: title is {len(title)} characters")

    def test_pages_with_a_visible_trail_publish_breadcrumb_markup(self):
        for path in ["/services/seo-optimization/", "/locations/nairobi/",
                     "/blog/website-cost-kenya/", reverse("core:web_development"),
                     reverse("core:privacy")]:
            body = self.client.get(path).content.decode()
            self.assertIn("BreadcrumbList", body, f"{path} has no breadcrumb markup")

    def test_every_page_offers_a_sharing_image(self):
        """A link with no image renders as a grey box on WhatsApp."""
        for path in self._pages():
            body = self.client.get(path).content.decode()
            match = re.search(r'<meta property="og:image" content="(.*?)"', body)
            self.assertIsNotNone(match, f"{path} has no og:image")
            self.assertTrue(
                match.group(1).startswith("http"),
                f"{path}: og:image is relative, which crawlers drop",
            )

    def test_a_from_price_is_never_published_as_exact(self):
        body = self.client.get("/services/seo-optimization/").content.decode()
        self.assertIn("minPrice", body)


class SeedCommandTests(TestCase):
    """The seeder used to empty its own definitions as it read them.

    `data.pop("slug")` on module-level constants mutated them in place, so a
    second run in the same process seeded rows with no slug — an IntegrityError
    on the unique column. Running it exactly once per process in the Render
    build is what kept it hidden.
    """

    def test_running_twice_in_one_process_is_safe(self):
        call_command("seed_content", verbosity=0)
        first = Package.objects.count()
        call_command("seed_content", verbosity=0)
        self.assertEqual(Package.objects.count(), first)
        self.assertFalse(
            Package.objects.filter(slug="").exists(),
            "a package was seeded without a slug",
        )

    def test_the_definitions_survive_being_read(self):
        from apps.core.management.commands.seed_content import (
            LOCATIONS, PACKAGES, SERVICES,
        )

        call_command("seed_content", verbosity=0)
        for name, definitions in (
            ("SERVICES", SERVICES), ("PACKAGES", PACKAGES), ("LOCATIONS", LOCATIONS)
        ):
            for definition in definitions:
                self.assertIn(
                    "slug", definition,
                    f"{name} lost its slug key — the seeder mutated its own constants",
                )
