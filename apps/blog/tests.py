from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import SiteSettings

from .models import BlogPost, Category
from .rendering import render_markdown


class MarkdownRenderingTests(TestCase):
    """The body is author-written, but it is still sanitised.

    The author is trusted; a compromised admin account is not. Sanitising costs
    nothing and stops one stolen password becoming a script in every reader's
    browser.
    """

    def test_headings_lists_and_links_render(self):
        html = render_markdown("## A section\n\n- one\n- two\n\nSee [services](/services/).")
        self.assertIn("<h2>A section</h2>", html)
        self.assertIn("<li>one</li>", html)
        self.assertIn('href="/services/"', html)

    def test_scripts_are_stripped(self):
        html = render_markdown("<script>alert('xss')</script>\n\nSafe.")
        self.assertNotIn("<script", html)
        self.assertIn("Safe.", html)

    def test_javascript_urls_are_stripped(self):
        html = render_markdown("[click](javascript:alert(1))")
        self.assertNotIn("javascript:", html)

    def test_event_handlers_are_stripped(self):
        html = render_markdown('<p onclick="steal()">Text</p>')
        self.assertNotIn("onclick", html)

    def test_h1_is_not_allowed(self):
        """The post title is the page's h1; a second one breaks the outline."""
        self.assertNotIn("<h1", render_markdown("# Nope"))

    def test_external_links_cannot_reach_back_through_opener(self):
        html = render_markdown("[Google](https://google.com)")
        self.assertIn('rel="noopener noreferrer"', html)
        self.assertIn('target="_blank"', html)

    def test_internal_links_are_left_alone(self):
        html = render_markdown("[About](/about/)")
        self.assertNotIn("target=", html)

    def test_tables_are_wrapped_so_they_cannot_push_the_page_sideways(self):
        html = render_markdown("| a | b |\n|---|---|\n| 1 | 2 |")
        self.assertIn("table-wrap", html)
        self.assertIn("<table", html)

    def test_empty_body_renders_nothing(self):
        self.assertEqual(render_markdown(""), "")
        self.assertEqual(render_markdown(None), "")


class PostBodyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()
        cls.author = User.objects.create_user(
            username="evans", password="x", first_name="Evans"
        )
        cls.category = Category.objects.create(name="SEO", slug="seo")
        cls.post = BlogPost.objects.create(
            title="A post with structure",
            slug="a-post",
            excerpt="Short summary.",
            body=(
                "Opening paragraph.\n\n"
                "## First section\n\n"
                "Body text with a [link](/packages/).\n\n"
                "## Second section\n\n"
                "More text.\n"
            ),
            author=cls.author,
            is_published=True,
            published_at=timezone.now(),
        )
        cls.post.categories.add(cls.category)

    def test_the_body_renders_its_headings_on_the_page(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertContains(response, "<h2>First section</h2>", html=False)
        self.assertContains(response, 'href="/packages/"')

    def test_reading_time_is_shown(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertContains(response, "min read")

    def test_contents_lists_the_sections(self):
        self.assertEqual(
            [entry["text"] for entry in self.post.contents],
            ["First section", "Second section"],
        )

    def test_reading_time_is_never_zero(self):
        short = BlogPost(body="Three words here.")
        self.assertEqual(short.reading_minutes, 1)

    def test_reading_time_scales_with_length(self):
        long_post = BlogPost(body=" ".join(["word"] * 1000))
        self.assertEqual(long_post.reading_minutes, 5)


class EmptyCategoryTests(TestCase):
    """An empty category was a dead end for readers and thin content for search."""

    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()
        cls.empty = Category.objects.create(name="Ads", slug="ads")

    def test_an_empty_category_is_not_linked_from_the_blog(self):
        response = self.client.get(reverse("blog:list"))
        self.assertNotContains(response, 'href="/blog/category/ads/"')

    def test_an_empty_category_page_is_not_indexed(self):
        response = self.client.get(self.empty.get_absolute_url())
        self.assertContains(response, "noindex")

    def test_an_empty_category_still_offers_somewhere_to_go(self):
        response = self.client.get(self.empty.get_absolute_url())
        self.assertContains(response, "rest of the blog")
        self.assertContains(response, "Get my free audit")
