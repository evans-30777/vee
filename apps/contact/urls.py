from django.urls import path

from . import views

app_name = "contact"

urlpatterns = [
    path("", views.contact, name="contact"),
    path("thank-you/", views.thank_you, name="thank_you"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
]
