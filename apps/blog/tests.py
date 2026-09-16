from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import SiteSettings

from .models import BlogPost, Category


class BlogPublishingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()
        cls.author = User.objects.create_user(username="evans", password="test-pass-123")
        cls.category = Category.objects.create(name="SEO & AEO", slug="seo-aeo")
        cls.live_post = BlogPost.objects.create(
            title="How to rank in Nairobi",
            slug="how-to-rank-in-nairobi",
            excerpt="A practical guide.",
            body="Body content.",
            author=cls.author,
            is_published=True,
        )
        cls.live_post.categories.add(cls.category)

    def test_publishing_sets_published_at_automatically(self):
        self.assertIsNotNone(self.live_post.published_at)

    def test_draft_posts_are_excluded_from_published_manager(self):
        BlogPost.objects.create(
            title="Draft",
            slug="draft",
            excerpt="x",
            body="x",
            author=self.author,
            is_published=False,
        )
        self.assertEqual(BlogPost.published.count(), 1)

    def test_future_dated_posts_are_excluded(self):
        BlogPost.objects.create(
            title="Scheduled",
            slug="scheduled",
            excerpt="x",
            body="x",
            author=self.author,
            is_published=True,
            published_at=timezone.now() + timedelta(days=3),
        )
        self.assertEqual(BlogPost.published.count(), 1)

    def test_draft_post_detail_returns_404(self):
        draft = BlogPost.objects.create(
            title="Hidden",
            slug="hidden",
            excerpt="x",
            body="x",
            author=self.author,
            is_published=False,
        )
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)

    def test_blog_pages_render(self):
        for url in [
            reverse("blog:list"),
            self.live_post.get_absolute_url(),
            self.category.get_absolute_url(),
            reverse("blog:author", kwargs={"username": "evans"}),
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_faq_schema_rendered_when_faqs_present(self):
        self.live_post.faqs = [{"question": "Is SEO fast?", "answer": "No, it compounds."}]
        self.live_post.save()
        response = self.client.get(self.live_post.get_absolute_url())
        self.assertContains(response, "FAQPage")
        self.assertContains(response, "Is SEO fast?")

    def test_quick_answer_rendered_when_present(self):
        self.live_post.quick_answer = "Optimise your Google Business Profile first."
        self.live_post.save()
        response = self.client.get(self.live_post.get_absolute_url())
        self.assertContains(response, "Optimise your Google Business Profile first.")
