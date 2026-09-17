from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.core.models import NewsletterSubscriber
from apps.core.seo import page_meta

from .forms import ContactForm, NewsletterForm
from .models import ContactSubmission
from .services import dispatch_enquiry_notifications
from .utils import get_client_ip, is_rate_limited

VALID_SERVICES = {choice.value for choice in ContactSubmission.Service}


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        ip_address = get_client_ip(request)

        if is_rate_limited(ip_address):
            messages.error(
                request,
                "You've sent several enquiries recently. Please call or WhatsApp us instead.",
            )
        elif form.is_valid():
            submission = form.save(commit=False)
            submission.ip_address = ip_address
            submission.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
            submission.save()
            dispatch_enquiry_notifications(submission)
            destination = reverse("contact:thank_you")
            if submission.service:
                destination = f"{destination}?service={submission.service}"
            return redirect(destination)
    else:
        # "Choose Plan" links prefill the form; only accept known service values.
        requested_service = request.GET.get("service", "")
        initial = {"service": requested_service} if requested_service in VALID_SERVICES else {}
        form = ContactForm(initial=initial)

    context = {
        "form": form,
        **page_meta(
            request,
            title="Contact VEE Agency — Book a Free Audit",
            description=(
                "Talk to VEE Agency about websites, SEO, Google Business Profile, "
                "social media and ads for your business in Nairobi, Machakos, "
                "Kajiado, Kiambu and across Kenya."
            ),
            page_class="contact",
        ),
    }
    return render(request, "contact/contact.html", context)


def thank_you(request):
    # Only ever a known choice: this value is published to analytics, and the
    # URL is user-controlled.
    requested_service = request.GET.get("service", "")
    context = {
        "enquiry_service": requested_service if requested_service in VALID_SERVICES else "",
        **page_meta(
            request,
            title="Thank You — VEE Agency",
            description="Your enquiry has reached VEE Agency. We'll be in touch shortly.",
            page_class="thank-you",
            noindex=True,
        ),
    }
    return render(request, "contact/thank_you.html", context)


@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if form.is_valid():
        NewsletterSubscriber.objects.update_or_create(
            email=form.cleaned_data["email"],
            defaults={
                "is_active": True,
                "source": form.cleaned_data.get("source", ""),
            },
        )
        message = "You're subscribed. Thanks for joining."
        success = True
    else:
        message = "Please enter a valid email address."
        success = False

    if is_ajax:
        return JsonResponse({"success": success, "message": message})

    messages.success(request, message) if success else messages.error(request, message)
    return redirect(request.META.get("HTTP_REFERER") or reverse("core:home"))
