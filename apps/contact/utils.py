from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import ContactSubmission


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def is_rate_limited(ip_address):
    """Limit submissions per IP per hour (technical guide section 8)."""
    if not ip_address:
        return False
    window_start = timezone.now() - timedelta(hours=1)
    recent = ContactSubmission.objects.filter(
        ip_address=ip_address,
        created_at__gte=window_start,
    ).count()
    return recent >= settings.CONTACT_RATE_LIMIT_PER_HOUR
