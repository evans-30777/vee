from django.db import models
from django.urls import reverse

from apps.core.models import TimeStampedModel


class Service(TimeStampedModel):
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True)
    icon = models.CharField(
        max_length=60,
        blank=True,
        help_text="Icon identifier used by the template layer.",
    )
    tagline = models.CharField(max_length=200, blank=True)
    short_description = models.TextField(help_text="Used on cards and listings.")
    full_description = models.TextField(blank=True)
    deliverables = models.JSONField(
        default=list,
        blank=True,
        help_text='List of deliverables, e.g. ["Keyword research", "On-page fixes"].',
    )
    starting_price = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Starting price in KES. Leave blank if quoted case-by-case.",
    )
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("services:detail", kwargs={"slug": self.slug})
