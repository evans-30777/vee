from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Author profile",
            {
                "fields": ("job_title", "bio", "headshot", "facebook", "instagram"),
                "description": "Shown on the About page and blog author page.",
            },
        ),
    )
