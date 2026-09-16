import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import CaseStudy, NewsletterSubscriber, SiteSettings, Testimonial


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Brand", {"fields": ("tagline", "default_social_image")}),
        (
            "Contact",
            {
                "fields": ("phone_calls", "whatsapp_number", "email", "location_label"),
                "description": "phone_calls is the click-to-call number. whatsapp_number builds wa.me links.",
            },
        ),
        (
            "Social",
            {
                "fields": ("facebook_url", "instagram_url"),
                "description": "Leave blank until a real URL exists — blank links are not rendered.",
            },
        ),
        ("Search", {"fields": ("service_counties",)}),
        (
            "Analytics",
            {
                "fields": (
                    "google_site_verification",
                    "ga4_measurement_id",
                    "meta_pixel_id",
                ),
                "description": (
                    "Leave blank to set no tracking cookies at all — the cookie consent "
                    "banner only appears once GA4 or the Meta Pixel is configured here. "
                    "Neither loads until a visitor accepts."
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "business", "is_featured", "is_active", "order")
    list_filter = ("is_active", "is_featured")
    list_editable = ("is_featured", "is_active", "order")
    search_fields = ("client_name", "business", "quote")
    ordering = ("order", "-created_at")


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ("client_label", "industry", "is_active", "order")
    list_filter = ("is_active", "industry")
    list_editable = ("is_active", "order")
    search_fields = ("client_label", "industry", "challenge", "solution", "result")
    prepopulated_fields = {"slug": ("client_label",)}
    ordering = ("order", "-created_at")
    fieldsets = (
        (None, {"fields": ("client_label", "slug", "industry", "featured_image")}),
        ("Story", {"fields": ("challenge", "solution", "result")}),
        (
            "Metrics",
            {
                "fields": ("metrics",),
                "description": "Only add metrics VEE can verify. Leave empty otherwise.",
            },
        ),
        ("Display", {"fields": ("order", "is_active")}),
    )


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "source", "created_at")
    list_filter = ("is_active", "source")
    search_fields = ("email",)
    ordering = ("-created_at",)
    actions = ("export_as_csv",)

    @admin.action(description="Export selected subscribers to CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=newsletter-subscribers.csv"
        writer = csv.writer(response)
        writer.writerow(["email", "is_active", "source", "subscribed_at"])
        for subscriber in queryset:
            writer.writerow(
                [
                    subscriber.email,
                    subscriber.is_active,
                    subscriber.source,
                    subscriber.created_at.isoformat(),
                ]
            )
        return response
