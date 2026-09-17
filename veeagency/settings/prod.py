"""Production settings. Every secret comes from the environment."""

from .base import *  # noqa: F403
from .base import BASE_DIR, os

DEBUG = False

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

# Render supplies the service's own hostname, which is not known until the
# service exists. Picking it up automatically means the staging deployment needs
# no hand-entered host, CSRF origin or base URL — three things that otherwise go
# wrong on first boot and present as a confusing 400 rather than a clear error.
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
if RENDER_HOSTNAME:
    # Normalise: ALLOWED_HOSTS entries must be bare hostnames. Django matches
    # against the host with the port already stripped, so an entry carrying a
    # scheme or a port silently never matches and every request 400s with
    # nothing useful in the message.
    render_origin = RENDER_HOSTNAME if "://" in RENDER_HOSTNAME else f"https://{RENDER_HOSTNAME}"
    RENDER_HOSTNAME = RENDER_HOSTNAME.split("://")[-1].split("/")[0].split(":")[0]

    if RENDER_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_HOSTNAME)

    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)

    # Canonical URLs must point at the host actually being served. Left pointing
    # at the live domain, a staging page would name a live URL as its canonical.
    if not os.environ.get("SITE_BASE_URL"):
        SITE_BASE_URL = render_origin

# SQLite in production: HostAfrica does not offer PostgreSQL, and this site's
# write volume (enquiries, newsletter signups, admin edits) is comfortably within
# what SQLite handles. Revisit if write concurrency ever becomes real.
#
# SQLITE_PATH must point OUTSIDE the public web root. If the database file is
# web-reachable, anyone can download every enquiry and password hash — see
# DEPLOYMENT.md.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("SQLITE_PATH") or BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            # WAL lets readers continue during a write, which is what stops a
            # single enquiry submission from blocking page views.
            # timeout makes a brief lock wait rather than raising
            # "database is locked" straight away.
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
            "timeout": 20,
        },
    }
}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
