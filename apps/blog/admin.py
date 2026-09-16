from django.contrib import admin

from .models import BlogPost, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_published")
    list_filter = ("is_published", "categories", "author")
    search_fields = ("title", "excerpt", "body", "quick_answer")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-created_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "categories")}),
        (
            "Quick Answer",
            {
                "fields": ("quick_answer",),
                "description": "Short, direct answer shown at the top of the post. Helps AEO and featured snippets.",
            },
        ),
        ("Content", {"fields": ("excerpt", "body", "featured_image", "featured_image_alt")}),
        (
            "FAQ",
            {
                "fields": ("faqs",),
                "description": 'List of {"question": "...", "answer": "..."} objects used for FAQ schema.',
            },
        ),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
        ("Publishing", {"fields": ("is_published", "published_at")}),
    )
