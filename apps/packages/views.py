from django.shortcuts import render

from apps.core.seo import page_meta

from .comparison import build_comparison
from .models import Package

# Answered only from facts already confirmed on the site. Contract length,
# cancellation terms and setup fees are the other questions buyers ask, and
# none of them are settled yet — inventing an answer here would be worse than
# leaving it out. See SITE_AUDIT.md.
PRICING_FAQS = [
    {
        "question": "Is advertising spend included in the price?",
        "answer": (
            "No. What you pay Google or Meta for the ads themselves is billed "
            "separately and goes straight to them — the package price is for "
            "managing the campaigns. You decide the media budget, and you can "
            "start a package without running ads at all."
        ),
    },
    {
        "question": "Who owns the website and the accounts?",
        "answer": (
            "You do. Your website, your domain, your Google Business Profile and "
            "your social accounts are all registered in your name, not ours. If "
            "you ever stop working with us, everything stays with you and nothing "
            "needs to be handed over."
        ),
    },
    {
        "question": "Is the website cost separate from the monthly packages?",
        "answer": (
            "Yes. A website is a one-time build from KES 30,000. The monthly "
            "packages are ongoing growth work — search visibility, Google "
            "Business Profile, social and ads. You can have either without the "
            "other, though they work better together."
        ),
    },
    {
        "question": "Do I need a website before starting a monthly package?",
        "answer": (
            "Not necessarily, but it changes what the package can achieve. "
            "Visibility work sends people somewhere — if there is nothing solid "
            "to send them to, you are paying to be found and then losing the "
            "enquiry. The free audit will tell you honestly whether the site "
            "needs to come first."
        ),
    },
    {
        "question": "What if I am not sure which package fits?",
        "answer": (
            "Take the free audit. You will get a straight recommendation based on "
            "what your business actually needs right now — including when the "
            "cheapest package is the right one, or when you would be better off "
            "fixing something yourself before paying for anything."
        ),
    },
]


def package_list(request):
    monthly = list(
        Package.objects.filter(is_active=True, billing_type=Package.BillingType.MONTHLY)
    )
    context = {
        "monthly_packages": monthly,
        "one_time_packages": Package.objects.filter(
            is_active=True, billing_type=Package.BillingType.ONE_TIME
        ),
        # None when the tiers are not the three the matrix describes, so an
        # extra package added in Admin drops the table rather than misreporting.
        "comparison": build_comparison(monthly),
        "pricing_faqs": PRICING_FAQS,
        **page_meta(
            request,
            title="Digital Growth Packages & Pricing in Kenya — VEE Agency",
            description=(
                "Monthly digital growth packages from KES 15,000 and websites from "
                "KES 30,000, priced up front, for businesses across Kenya."
            ),
            page_class="packages",
        ),
    }
    return render(request, "packages/package_list.html", context)
