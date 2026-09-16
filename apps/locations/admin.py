from django.contrib import admin

from .models import LocationPage


@admin.register(LocationPage)
class LocationPageAdmin(admin.ModelAdmin):
    list_display = ("county", "order", "is_active")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("county", "hero_headline", "intro", "body")
    prepopulated_fields = {"slug": ("county",)}
    filter_horizontal = ("featured_services",)
    ordering = ("order", "county")
    fieldsets = (
        (None, {"fields": ("county", "slug")}),
        ("Content", {"fields": ("hero_headline", "intro", "body", "featured_services")}),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description"),
                "description": "Write naturally — do not stuff county names.",
            },
        ),
        ("Display", {"fields": ("order", "is_active")}),
    )
