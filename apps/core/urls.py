from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("case-studies/", views.case_studies, name="case_studies"),
    path("web-development/", views.web_development, name="web_development"),
    path("legal/privacy/", views.legal_page, {"doc": "privacy"}, name="privacy"),
    path("legal/terms/", views.legal_page, {"doc": "terms"}, name="terms"),
    path("legal/cookies/", views.legal_page, {"doc": "cookies"}, name="cookies"),
    path("legal/disclaimer/", views.legal_page, {"doc": "disclaimer"}, name="disclaimer"),
]
