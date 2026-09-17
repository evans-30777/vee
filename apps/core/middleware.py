"""Response headers that are easier to set here than per-view."""

from django.conf import settings


class SecurityHeadersMiddleware:
    """Content-Security-Policy and Permissions-Policy.

    CSP matters here specifically because the site injects third-party scripts
    after consent: it is the control that guarantees nothing *else* can ever be
    injected, including through a compromised admin account writing into a blog
    body.

    The policy is deliberately narrow. Everything comes from this origin — the
    fonts are self-hosted and there is no third-party CSS — so the only outside
    origins named are the analytics endpoints, and only because the visitor may
    have consented to them.
    """

    ANALYTICS_SCRIPT = (
        "https://www.googletagmanager.com "
        "https://connect.facebook.net"
    )
    ANALYTICS_CONNECT = (
        "https://www.google-analytics.com "
        "https://*.google-analytics.com "
        "https://*.analytics.google.com "
        "https://www.googletagmanager.com "
        "https://connect.facebook.net "
        "https://www.facebook.com"
    )
    ANALYTICS_IMG = (
        "https://www.google-analytics.com "
        "https://*.google-analytics.com "
        "https://www.googletagmanager.com "
        "https://www.facebook.com"
    )

    def __init__(self, get_response):
        self.get_response = get_response
        self.policy = self.build_policy()
        self.permissions = (
            "geolocation=(), microphone=(), camera=(), payment=(), usb=(), "
            "magnetometer=(), gyroscope=(), interest-cohort=()"
        )

    def build_policy(self):
        directives = [
            "default-src 'self'",
            # 'unsafe-inline' is required by the analytics snippets themselves
            # and by the class-swap script that runs before first paint. A
            # nonce would be better and is a worthwhile follow-up; it needs the
            # inline blocks moved behind a template tag first.
            f"script-src 'self' 'unsafe-inline' {self.ANALYTICS_SCRIPT}",
            "style-src 'self' 'unsafe-inline'",
            "font-src 'self'",
            f"img-src 'self' data: {self.ANALYTICS_IMG}",
            f"connect-src 'self' {self.ANALYTICS_CONNECT}",
            "frame-src 'none'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
        ]
        if not settings.DEBUG:
            directives.append("upgrade-insecure-requests")
        return "; ".join(directives)

    def __call__(self, request):
        response = self.get_response(request)
        # Never override the admin's own needs, and never touch a streamed file.
        if not request.path.startswith("/admin/"):
            response.setdefault("Content-Security-Policy", self.policy)
        response.setdefault("Permissions-Policy", self.permissions)
        return response
