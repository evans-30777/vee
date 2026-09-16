from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


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
        return super().save(*args, **kwargs)

    @property
    def whatsapp_url(self):
        return f"https://wa.me/{self.whatsapp_number}"

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
