from django.shortcuts import render


def handler404(request, exception=None):
    return render(request, "404.html", status=404)


def handler500(request):
    # Rendered without extra context so a failing view cannot cascade into the error page.
    return render(request, "500.html", status=500)
