from django.shortcuts import render

from .seo import page_meta


def handler404(request, exception=None):
    # Given real metadata so the page is a proper document rather than a
    # titleless shell, and noindex so a missing URL never enters the index.
    context = page_meta(
        request,
        title="Page not found — VEE Agency",
        description="That page doesn't exist. Find VEE Agency's services, packages and contact details here.",
        page_class="error",
        noindex=True,
    )
    return render(request, "404.html", context, status=404)


def handler500(request):
    # Rendered without extra context so a failing view cannot cascade into the error page.
    return render(request, "500.html", status=500)
