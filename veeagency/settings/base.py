"""Shared settings for the VEE Agency site."""

from pathlib import Path

from dotenv import load_dotenv
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
DEBUG = False
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "apps.accounts",
    "apps.core",
    "apps.services",
    "apps.packages",
    "apps.blog",
    "apps.locations",
    "apps.contact",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "veeagency.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "veeagency.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-ke"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
# Configurable so uploads can be pointed at a persistent volume; on hosts with
# an ephemeral filesystem, the project directory does not survive a redeploy.
MEDIA_ROOT = os.environ.get("MEDIA_ROOT") or BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# In-process cache. Enough for a single-server SQLite site: the only thing
# cached is the SiteSettings singleton, which the context processor otherwise
# re-queries on every single request.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "vee-default",
    }
}

# A local-memory cache is process-global and is NOT rolled back between tests,
# unlike the database — so a value cached by one test outlives the row it came
# from and the next test reads a ghost. Tests therefore run uncached, and the
# caching behaviour itself is covered by its own test that opts back in.
if "test" in sys.argv:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "https://veeagency.co.ke")

# Staging mode. Set on any deployment that is not veeagency.co.ke.
#
# A public copy of the site is a real SEO hazard: left crawlable, Google indexes
# it as a duplicate of the live site and the two compete with each other. With
# this on, every page sends noindex, robots.txt disallows everything, and a
# banner makes clear the site is not live.
SITE_IS_STAGING = os.environ.get("SITE_IS_STAGING", "false").lower() == "true"

# Bound how long a stalled mail host can hold a socket. Python's default is no
# timeout at all, which is what turns a slow SMTP server into a hung request.
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "10"))

# Send enquiry mail on a background thread. Off here so development and tests
# stay synchronous and deterministic; production turns it on.
EMAIL_SEND_ASYNC = False

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "hello@veeagency.co.ke")
ENQUIRY_NOTIFICATION_EMAIL = os.environ.get(
    "ENQUIRY_NOTIFICATION_EMAIL", "hello@veeagency.co.ke"
)

# Public form abuse controls (see technical guide section 8).
#
# Kenyan mobile networks use carrier-grade NAT, so a single public address can
# be shared by a great many real people. Three an hour was low enough that a
# genuine customer on a busy Safaricom IP could be turned away; six still stops
# automated abuse.
CONTACT_RATE_LIMIT_PER_HOUR = int(os.environ.get("CONTACT_RATE_LIMIT_PER_HOUR", "6"))

# How many proxies sit in front of this app and can be trusted to have appended
# a real address to X-Forwarded-For. 0 means read REMOTE_ADDR only. Render and
# HostAfrica both terminate TLS in front of the app, so production sets 1.
CONTACT_TRUSTED_PROXY_COUNT = int(os.environ.get("CONTACT_TRUSTED_PROXY_COUNT", "0"))

# More generous than the enquiry limit: a shared office or carrier address can
# legitimately produce several signups, and a false positive only costs a
# newsletter subscription.
NEWSLETTER_RATE_LIMIT_PER_HOUR = int(os.environ.get("NEWSLETTER_RATE_LIMIT_PER_HOUR", "10"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
