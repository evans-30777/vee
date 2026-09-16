from django.contrib import admin

from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("name", "billing_type", "price", "reference_price", "is_highlighted", "order", "is_active")
    list_filter = ("billing_type", "is_active", "is_highlighted")
    list_editable = ("order", "is_active", "is_highlighted")
    search_fields = ("name", "short_description", "ideal_for")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "price")
    fieldsets = (
        (None, {"fields": ("name", "slug", "billing_type", "short_description", "ideal_for")}),
        (
            "Pricing",
            {
                "fields": ("price", "reference_price", "price_is_from"),
                "description": "Prices in KES. reference_price shows struck through. Tick 'price is from' for starting prices.",
            },
        ),
        ("Features", {"fields": ("features",)}),
        ("Display", {"fields": ("is_highlighted", "order", "is_active")}),
    )
