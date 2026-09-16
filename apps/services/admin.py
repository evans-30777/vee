from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "starting_price", "order", "is_active")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("name", "tagline", "short_description", "full_description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
    fieldsets = (
        (None, {"fields": ("name", "slug", "icon", "tagline")}),
        ("Content", {"fields": ("short_description", "full_description", "deliverables")}),
        (
            "Pricing",
            {
                "fields": ("starting_price",),
                "description": "Starting price in KES. Leave blank when quoted case-by-case.",
            },
        ),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description"),
                "description": "Include location relevance (Nairobi, Machakos, Kajiado, Kiambu, Kenya) where natural.",
            },
        ),
        ("Display", {"fields": ("order", "is_active")}),
    )
