from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from django.utils.functional import cached_property

from apps.blog.rendering import render_markdown, table_of_contents
from apps.core.imaging import optimise_image_field
from apps.core.models import FEATURE_IMAGE_MAX, TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_published=True, published_at__lte=timezone.now())
        )


class BlogPost(TimeStampedModel):
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    excerpt = models.TextField(help_text="Short summary used on listings and cards.")
    quick_answer = models.TextField(
        blank=True,
        help_text="Direct answer shown in the Quick Answer box, for AEO/featured snippets.",
    )
    body = models.TextField(
        help_text=(
            "Markdown. Use ## for subheadings, - for bullets, **bold**, and "
            "[text](/services/) to link to other pages on the site."
        )
    )
    featured_image = models.ImageField(upload_to="blog/", blank=True)
    featured_image_alt = models.CharField(max_length=200, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="posts",
    )
    categories = models.ManyToManyField(Category, blank=True, related_name="posts")
    faqs = models.JSONField(
        default=list,
        blank=True,
        help_text='List of {"question": ..., "answer": ...} used for FAQ schema.',
    )
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @cached_property
    def body_html(self):
        """The body as sanitised HTML.

        Rendered per request rather than stored: posts are read far more often
        than written, but the render is cheap and storing it would mean a
        migration every time the allowed-tag list changes.
        """
        return render_markdown(self.body)

    @cached_property
    def contents(self):
        return table_of_contents(self.body_html)

    @cached_property
    def reading_minutes(self):
        """Rounded up, minimum one. 200 words a minute is the usual estimate."""
        words = len(self.body.split())
        return max(1, round(words / 200))

    def save(self, *args, **kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        optimise_image_field(
            self.featured_image,
            max_width=FEATURE_IMAGE_MAX[0],
            max_height=FEATURE_IMAGE_MAX[1],
        )
        return super().save(*args, **kwargs)
