import html
import json
import re
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User
from apps.packages.models import Package
from apps.services.models import Service

from .models import SiteSettings, Testimonial
from .views import HERO_SLIDES


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
        self.assertContains(response, "hero__slide is-active")
        # One slide, one caption and one dot per clip — counted from the view's
        # own list rather than a hard-coded number, so adding or dropping a clip
        # cannot leave the controls out of step with the media.
        count = len(HERO_SLIDES)
        self.assertContains(response, 'aria-roledescription="slide"', count=count)
        self.assertContains(response, "data-slide-caption", count=count)
        self.assertContains(response, "data-dot", count=count)

    def test_hero_videos_offer_every_framing_codec_and_poster(self):
        """A phone gets the portrait cut, and every slide falls back to a still.

        The <video> elements deliberately carry no `src`: main.js chooses the
        framing and the codec. If that regressed to a hard-coded source, a phone
        would download the landscape file and show the wrong crop, and a browser
        without H.264 would show nothing at all.
        """
        response = self.client.get(reverse("core:home"))
        page = response.content.decode()
        for slide in HERO_SLIDES:
            name = slide["name"]
            for asset in [
                f"hero-{name}-wide.mp4",
                f"hero-{name}-wide.webm",
                f"hero-{name}-tall.mp4",
                f"hero-{name}-tall.webm",
                f"hero-{name}-poster-wide.jpg",
                f"hero-{name}-poster-tall.jpg",
            ]:
                with self.subTest(asset=asset):
                    self.assertIn(asset, page)
                    self.assertTrue(
                        (Path(settings.BASE_DIR) / "static" / "video" / asset).exists(),
                        f"{asset} is referenced but was never built",
                    )
        self.assertNotIn("<video class=\"hero__video\" src=", page)

    def test_poster_media_query_matches_the_framing_the_script_picks(self):
        """The CSS still and the JS video must agree on which crop to use.

        They are two independent breakpoints for one decision. Drifting apart
        means the poster shows one framing and the video dissolves into another.
        """
        static_dir = Path(settings.BASE_DIR) / "static"
        css = (static_dir / "css" / "main.css").read_text()
        js = (static_dir / "js" / "main.js").read_text()
        query = "(max-aspect-ratio: 5/4)"
        self.assertIn(f"@media {query}", css)
        self.assertIn(query, js)

    def test_hero_slide_durations_match_the_encoded_clips(self):
        """Each slide holds for its clip's real length.

        These files are built by `tools/build_hero_video.py`. If a clip is
        re-cut to a different length and HERO_SLIDES is not updated with it,
        the hero either cuts away mid-clip or sits on a frozen frame.
        """
        import subprocess

        import imageio_ffmpeg

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        for slide in HERO_SLIDES:
            path = (
                Path(settings.BASE_DIR)
                / "static"
                / "video"
                / f"hero-{slide['name']}-wide.mp4"
            )
            self.assertTrue(path.exists(), f"missing encoded clip: {path}")
            probe = subprocess.run(
                [ffmpeg, "-i", str(path)], capture_output=True, text=True
            ).stderr
            stamp = probe.split("Duration: ")[1].split(",")[0]
            hours, minutes, seconds = stamp.split(":")
            actual_ms = (int(hours) * 3600 + int(minutes) * 60 + float(seconds)) * 1000
            self.assertAlmostEqual(
                actual_ms,
                slide["duration"],
                delta=350,
                msg=(
                    f"{slide['name']}: the clip runs {actual_ms:.0f}ms but "
                    f"HERO_SLIDES says {slide['duration']}ms"
                ),
            )

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


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "sitesettings-cache-test",
        }
    }
)
class SiteSettingsCacheTests(TestCase):
    """The singleton is read on every request by the context processor.

    Tests run against a dummy cache, so this class opts back in to a real one
    and clears it itself — otherwise the values would outlive the rows they
    came from, which is the reason tests are uncached in the first place.
    """

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)

    def test_the_singleton_is_only_queried_once(self):
        SiteSettings.objects.create()
        SiteSettings.load()
        with self.assertNumQueries(0):
            SiteSettings.load()
            SiteSettings.load()

    def test_saving_shows_up_immediately(self):
        current = SiteSettings.objects.create()
        SiteSettings.load()

        current.tagline = "A brand new tagline."
        current.save()

        self.assertEqual(SiteSettings.load().tagline, "A brand new tagline.")

    def test_having_no_settings_row_is_cached_too(self):
        """Otherwise a missing row costs a query on every single request."""
        self.assertIsNone(SiteSettings.load())
        with self.assertNumQueries(0):
            self.assertIsNone(SiteSettings.load())

    def test_creating_the_first_row_invalidates_the_empty_result(self):
        self.assertIsNone(SiteSettings.load())
        SiteSettings.objects.create(tagline="Now it exists.")
        self.assertIsNotNone(SiteSettings.load())


class TemplateSyntaxLeakTests(TestCase):
    """No template syntax may reach the page.

    Django's `{# #}` comment is single-line only: written across two lines it
    is not a comment at all and renders as literal text. Three of them shipped
    — on the home, contact and blog post pages — and visitors saw the raw
    comment. Nothing in the test suite noticed, because every check was about
    structure, not about what the words on the page actually said.
    """

    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()
        User.objects.create_superuser(
            username="evans", email="hello@veeagency.co.ke", password="x",
            first_name="Evans",
        )
        call_command("seed_content", "--with-posts", verbosity=0)

    def _all_pages(self):
        return [
            reverse("core:home"), reverse("core:about"), reverse("core:case_studies"),
            reverse("core:web_development"), reverse("services:list"),
            reverse("packages:list"), reverse("blog:list"), reverse("locations:list"),
            reverse("contact:contact"), reverse("contact:thank_you"),
            reverse("core:privacy"), reverse("core:terms"), reverse("core:cookies"),
            reverse("core:disclaimer"),
            "/services/seo-optimization/", "/locations/nairobi/",
            "/blog/website-cost-kenya/", "/blog/category/seo-aeo/",
            "/blog/author/evans/",
        ]

    def test_no_unrendered_template_syntax_on_any_page(self):
        for path in self._all_pages():
            body = self.client.get(path).content.decode()
            visible = body.split("<body", 1)[1] if "<body" in body else body
            for token, what in (("{#", "an unclosed {# #} comment"),
                                ("#}", "the end of a {# #} comment"),
                                ("{%", "a template tag"),
                                ("{{", "a template variable")):
                self.assertNotIn(
                    token, visible,
                    f"{path} renders {what} as visible text — look for a "
                    f"{{# #}} comment written across more than one line.",
                )

    def test_the_source_has_no_multi_line_hash_comments(self):
        """Catches the mistake at its source, not just where it surfaced."""
        import re
        from pathlib import Path

        offenders = []
        for template in Path(settings.BASE_DIR, "templates").rglob("*.html"):
            text = template.read_text()
            for match in re.finditer(r"\{#", text):
                end = text.find("\n", match.start())
                line = text[match.start():end if end != -1 else len(text)]
                if "#}" not in line:
                    offenders.append(f"{template.name}:{text[:match.start()].count(chr(10)) + 1}")
        self.assertEqual(
            offenders, [],
            "Django's {# #} comment is single-line only. Use {% comment %} for "
            f"anything longer. Found: {offenders}",
        )


class StylesheetIntegrityTests(TestCase):
    """A stylesheet with an unbalanced brace silently discards the rest of itself.

    An unclosed rule swallowed everything after it, so a whole block of
    small-screen overrides was parsed as part of a broken selector and never
    applied. Nothing failed loudly — the page just kept the old sizes.
    """

    def _css(self):
        from pathlib import Path
        return Path(settings.BASE_DIR, "static", "css", "main.css").read_text()

    def _without_comments(self):
        import re
        return re.sub(r"/\*.*?\*/", "", self._css(), flags=re.S)

    def test_braces_balance(self):
        body = self._without_comments()
        opens, closes = body.count("{"), body.count("}")
        self.assertEqual(
            opens, closes,
            f"main.css has {opens} opening and {closes} closing braces — "
            f"everything after the unclosed rule is being discarded.",
        )

    def test_no_rule_closes_before_it_opens(self):
        depth = 0
        for line_number, line in enumerate(self._without_comments().splitlines(), 1):
            for char in line:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth < 0:
                        self.fail(f"main.css line {line_number}: stray closing brace")

    def test_every_custom_property_used_is_defined(self):
        import re

        css = self._css()
        defined = set(re.findall(r"^\s*(--[a-zA-Z0-9-]+)\s*:", css, re.M))
        used = set(re.findall(r"var\(\s*(--[a-zA-Z0-9-]+)", css))
        # Supplied at runtime rather than in the stylesheet: --cookie-banner-height
        # is set by main.js, and the two poster URLs are written onto each
        # <video> as an inline style because they differ per slide. Both poster
        # rules sit on a declaration that also sets `background-color`, so a
        # missing value degrades to flat near-black rather than nothing.
        runtime = {"--poster-wide", "--poster-tall", "--cookie-banner-height"}
        missing = sorted(used - defined - runtime)
        self.assertEqual(missing, [], f"used but never defined: {missing}")
