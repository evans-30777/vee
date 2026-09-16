from django.shortcuts import render

from apps.core.seo import page_meta

from .models import Package


def package_list(request):
    context = {
        "monthly_packages": Package.objects.filter(
            is_active=True, billing_type=Package.BillingType.MONTHLY
        ),
        "one_time_packages": Package.objects.filter(
            is_active=True, billing_type=Package.BillingType.ONE_TIME
        ),
        **page_meta(
            request,
            title="Digital Growth Packages & Pricing in Kenya — VEE Agency",
            description=(
                "Monthly digital growth packages from KES 15,000 and website development "
                "from KES 30,000 for businesses in Nairobi, Machakos, Kajiado, Kiambu "
                "and across Kenya."
            ),
            page_class="packages",
        ),
    }
    return render(request, "packages/package_list.html", context)
