from django.core.exceptions import ValidationError
from django.db import models
from django.templatetags.static import static
from django.utils.text import slugify

from .imaging import optimise_image_field
from .seo import DEFAULT_SOCIAL_IMAGE

# Ceilings per image role. A social image only ever renders at Open Graph size,
# and a client logo only ever renders small, so neither needs more.
SOCIAL_IMAGE_MAX = (1200, 1200)
LOGO_MAX = (400, 400)
FEATURE_IMAGE_MAX = (1600, 1600)


def default_service_counties():
    return ["Nairobi", "Machakos", "Kajiado", "Kiambu"]


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(TimeStampedModel):
    """Singleton holding contact details and global site content."""

    tagline = models.CharField(
        max_length=200,
        default="Let's grow your brand online together.",
    )
    phone_calls = models.CharField(
        max_length=20,
        default="0717115737",
        help_text="Public number for voice calls (click-to-call).",
    )
    whatsapp_number = models.CharField(
        max_length=20,
        default="254759643882",
        help_text="International format without '+'. Used to build wa.me links.",
    )
    email = models.EmailField(default="hello@veeagency.co.ke")
    location_label = models.CharField(
        max_length=120,
        default="Syokimau, Machakos County, Kenya",
    )
    service_counties = models.JSONField(
        default=default_service_counties,
        blank=True,
        help_text="Counties with stronger local emphasis. Coverage is nationwide regardless.",
    )
    facebook_url = models.URLField(
        blank=True,
        help_text="Leave blank until the real profile URL is available; the icon stays hidden.",
    )
    instagram_url = models.URLField(
        blank=True,
        help_text="Leave blank until the real profile URL is available; the icon stays hidden.",
    )
    default_social_image = models.ImageField(
        upload_to="site/",
        blank=True,
        help_text="Fallback Open Graph image used when a page has none.",
    )

    google_site_verification = models.CharField(
        max_length=120,
        blank=True,
        help_text=(
            "Google Search Console verification token (the content value only, "
            "not the whole meta tag). Sets no cookie, so it needs no consent."
        ),
    )
    ga4_measurement_id = models.CharField(
        max_length=40,
        blank=True,
        help_text="Google Analytics 4 ID, e.g. G-XXXXXXXXXX. Only loads after cookie consent.",
    )
    meta_pixel_id = models.CharField(
        max_length=40,
        blank=True,
        help_text="Meta (Facebook) Pixel ID. Only loads after cookie consent.",
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def clean(self):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("Only one SiteSettings record may exist. Edit the existing one.")

    def save(self, *args, **kwargs):
        self.full_clean()
        optimise_image_field(
            self.default_social_image,
            max_width=SOCIAL_IMAGE_MAX[0],
            max_height=SOCIAL_IMAGE_MAX[1],
        )
        return super().save(*args, **kwargs)

    @property
    def whatsapp_url(self):
        return f"https://wa.me/{self.whatsapp_number}"

    @property
    def social_image_url(self):
        """Absolute URL of the sharing card, falling back to the brand default.

        Absolute because Open Graph and Twitter fetch the image server-side with
        no page context, so a relative path is silently dropped and the share
        renders as a bare link.
        """
        from .seo import absolute_url

        if self.default_social_image:
            return absolute_url(self.default_social_image.url)
        return absolute_url(static(DEFAULT_SOCIAL_IMAGE))

    @property
    def sets_optional_cookies(self):
        """Whether anything on the site needs consent.

        With no analytics configured the site sets only essential cookies, so
        showing a consent banner would be both pointless and untrue.
        """
        return bool(self.ga4_measurement_id or self.meta_pixel_id)

    @property
    def phone_calls_e164(self):
        """Click-to-call value, normalised however the number was entered.

        The field accepts the local form owners actually type ("0717 115 737"),
        but `tel:` links are more reliable in international format.
        """
        digits = "".join(char for char in self.phone_calls if char.isdigit())
        if digits.startswith("0"):
            digits = f"254{digits[1:]}"
        elif not digits.startswith("254"):
            digits = f"254{digits}"
        return f"+{digits}"

    @classmethod
    def load(cls):
        return cls.objects.first()


class Testimonial(TimeStampedModel):
    client_name = models.CharField(max_length=120)
    business = models.CharField(max_length=160, blank=True)
    quote = models.TextField()
    logo = models.ImageField(upload_to="testimonials/", blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.client_name} — {self.business}" if self.business else self.client_name

    def save(self, *args, **kwargs):
        optimise_image_field(self.logo, max_width=LOGO_MAX[0], max_height=LOGO_MAX[1])
        return super().save(*args, **kwargs)


class CaseStudy(TimeStampedModel):
    client_label = models.CharField(
        max_length=160,
        help_text="How the client is described publicly. Use a real, approved label.",
    )
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    industry = models.CharField(max_length=120, blank=True)
    challenge = models.TextField()
    solution = models.TextField()
    result = models.TextField()
    metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Only include metrics VEE can verify.",
    )
    featured_image = models.ImageField(upload_to="case-studies/", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name_plural = "Case studies"

    def __str__(self):
        return self.client_label

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.client_label)[:180]
        optimise_image_field(
            self.featured_image,
            max_width=FEATURE_IMAGE_MAX[0],
            max_height=FEATURE_IMAGE_MAX[1],
        )
        return super().save(*args, **kwargs)


class NewsletterSubscriber(TimeStampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(
        max_length=80,
        blank=True,
        help_text="Where the subscription came from, e.g. 'home', 'blog-post'.",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
