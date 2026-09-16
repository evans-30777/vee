from django.db import models

from apps.core.models import TimeStampedModel


class ContactSubmission(TimeStampedModel):
    class Service(models.TextChoices):
        ESSENTIAL = "essential", "Essential Growth"
        STANDARD = "standard", "Standard Growth"
        PREMIUM = "premium", "Premium Growth"
        WEBSITE = "website", "Website Development"
        OTHER = "other", "Something else"

    class Budget(models.TextChoices):
        UNDER_15K = "under_15k", "Under KES 15,000"
        K15_25 = "15k_25k", "KES 15,000–25,000"
        K25_45 = "25k_45k", "KES 25,000–45,000"
        K45_PLUS = "45k_plus", "KES 45,000+"
        UNSURE = "unsure", "Not sure yet"

    name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    service = models.CharField(max_length=20, choices=Service.choices, blank=True)
    budget = models.CharField(max_length=20, choices=Budget.choices, blank=True)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    is_processed = models.BooleanField(default=False)
    notification_sent = models.BooleanField(
        default=False,
        help_text="Whether the admin notification email was delivered successfully.",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
