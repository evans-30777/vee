from django.contrib import admin

from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "budget", "is_processed", "notification_sent", "created_at")
    list_filter = ("is_processed", "notification_sent", "service", "budget")
    list_editable = ("is_processed",)
    search_fields = ("name", "email", "phone", "message")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = (
        "name",
        "email",
        "phone",
        "service",
        "budget",
        "message",
        "ip_address",
        "user_agent",
        "notification_sent",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        ("Enquiry", {"fields": ("name", "email", "phone", "service", "budget", "message")}),
        ("Handling", {"fields": ("is_processed", "notification_sent")}),
        ("Request metadata", {"fields": ("ip_address", "user_agent", "created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        return False
