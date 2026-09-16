from django.db import models

from apps.core.models import TimeStampedModel


class Package(TimeStampedModel):
    """Monthly growth retainers and one-time services (e.g. website development)."""

    class BillingType(models.TextChoices):
        MONTHLY = "monthly", "Monthly retainer"
        ONE_TIME = "one_time", "One-time service"

    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True)
    billing_type = models.CharField(
        max_length=20,
        choices=BillingType.choices,
        default=BillingType.MONTHLY,
    )
    price = models.PositiveIntegerField(help_text="Current price in KES.")
    reference_price = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Original/reference price in KES, shown struck through. Optional.",
    )
    price_is_from = models.BooleanField(
        default=False,
        help_text="Show the price as a starting point, e.g. 'from KES 30,000'.",
    )
    short_description = models.TextField(blank=True)
    features = models.JSONField(
        default=list,
        blank=True,
        help_text="List of included features, in display order.",
    )
    ideal_for = models.CharField(max_length=240, blank=True)
    is_highlighted = models.BooleanField(
        default=False,
        help_text="Visually emphasise this package (e.g. the Premium tier).",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "price"]

    def __str__(self):
        return self.name
