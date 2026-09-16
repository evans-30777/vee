from django.db import models
from django.urls import reverse

from apps.core.models import TimeStampedModel


class LocationPage(TimeStampedModel):
    """Localised landing page for a county VEE Agency emphasises in local search."""

    county = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    hero_headline = models.CharField(max_length=200)
    intro = models.TextField()
    body = models.TextField(blank=True)
    featured_services = models.ManyToManyField(
        "services.Service",
        blank=True,
        related_name="location_pages",
    )
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "county"]

    def __str__(self):
        return self.county

    def get_absolute_url(self):
        return reverse("locations:detail", kwargs={"slug": self.slug})
