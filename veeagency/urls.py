from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from apps.core.sitemaps import SITEMAPS

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("services/", include("apps.services.urls")),
    path("packages/", include("apps.packages.urls")),
    path("blog/", include("apps.blog.urls")),
    path("locations/", include("apps.locations.urls")),
    path("contact/", include("apps.contact.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="django.contrib.sitemaps.views.sitemap"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
]

handler404 = "apps.core.views_errors.handler404"
handler500 = "apps.core.views_errors.handler500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
