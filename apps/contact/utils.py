from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.core.models import NewsletterSubscriber

from .models import ContactSubmission


def get_client_ip(request):
    """The client's address, trusting only as many proxies as we actually have.

    X-Forwarded-For is appended to by every hop, so the client-controlled part
    is on the *left* and the trustworthy part on the right. Taking the leftmost
    value let anyone send a random address per request and bypass the rate
    limit entirely.

    CONTACT_TRUSTED_PROXY_COUNT says how many hops in front of us we control
    (Render and HostAfrica both put one in front). We take the address that
    many places from the right — the one our own edge observed — and fall back
    to REMOTE_ADDR when the header is shorter than expected.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    remote = request.META.get("REMOTE_ADDR")

    trusted = getattr(settings, "CONTACT_TRUSTED_PROXY_COUNT", 0)
    if not forwarded or trusted < 1:
        return remote

    hops = [part.strip() for part in forwarded.split(",") if part.strip()]
    if len(hops) < trusted:
        # Fewer hops than configured: the header did not come the way we
        # expect, so it is not evidence of anything.
        return remote
    return hops[-trusted]


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


def is_newsletter_rate_limited(ip_address):
    """Signups per IP per hour.

    Separate from the enquiry limit and more generous: a shared office or
    mobile-carrier address can legitimately produce several signups, and the
    cost of a false positive here is only a newsletter.
    """
    if not ip_address:
        return False
    window_start = timezone.now() - timedelta(hours=1)
    recent = NewsletterSubscriber.objects.filter(
        signup_ip=ip_address, created_at__gte=window_start
    ).count()
    return recent >= settings.NEWSLETTER_RATE_LIMIT_PER_HOUR
