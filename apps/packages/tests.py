from django.test import TestCase
from django.urls import reverse

from apps.core.management.commands.seed_content import PACKAGES
from apps.core.models import SiteSettings

from .comparison import COMPARISON_ROWS, FEATURE_TO_ROW, build_comparison
from .models import Package


def seed_packages():
    """Build the real shipped packages, straight from the seed definitions.

    Using the seed data rather than invented fixtures is the point: these tests
    guard the content that actually goes live, so editing a feature list without
    updating the comparison matrix fails here.
    """
    for data in PACKAGES:
        Package.objects.create(**data)


class ComparisonMatrixTests(TestCase):
    """The comparison table is only useful while it matches the packages.

    It is a hand-built matrix rather than a union of the three feature lists,
    because several features are upgrades of one capability rather than extra
    items — "Basic website audit" and "Full website audit & revamp plan" are one
    row, not two. That accuracy has to be defended: a feature added in Admin
    without a matching row would otherwise vanish from the comparison silently.
    """

    @classmethod
    def setUpTestData(cls):
        seed_packages()

    def test_every_mapped_feature_points_at_a_real_row(self):
        row_labels = {label for label, _, _ in COMPARISON_ROWS}
        for feature, row in FEATURE_TO_ROW.items():
            self.assertIn(
                row, row_labels,
                f"'{feature}' maps to '{row}', which is not a row in the table",
            )

    def test_no_monthly_package_feature_is_missing_from_the_matrix(self):
        monthly = Package.objects.filter(
            is_active=True, billing_type=Package.BillingType.MONTHLY
        )
        self.assertTrue(monthly.exists())
        for package in monthly:
            for feature in package.features:
                self.assertIn(
                    feature, FEATURE_TO_ROW,
                    f"{package.name} lists '{feature}', which the comparison table "
                    f"does not account for. Add it to FEATURE_TO_ROW and to a row "
                    f"in COMPARISON_ROWS.",
                )

    def test_tiers_are_cumulative(self):
        """Owner decision, 2026-09-17: each tier includes the one below it."""
        comparison = build_comparison(
            list(Package.objects.filter(is_active=True, billing_type="monthly"))
        )
        self.assertIsNotNone(comparison)
        for row in comparison["rows"]:
            included = [cell["included"] for cell in row["cells"]]
            for cheaper, dearer in zip(included, included[1:]):
                self.assertFalse(
                    cheaper and not dearer,
                    f"'{row['label']}' is included in a cheaper tier but not a dearer one",
                )

    def test_table_is_dropped_when_the_tiers_are_not_the_three_it_describes(self):
        """A fourth package should remove the table, not render a wrong one."""
        Package.objects.create(
            name="Enterprise Growth", slug="enterprise", price=90000,
            billing_type=Package.BillingType.MONTHLY,
        )
        monthly = list(
            Package.objects.filter(is_active=True, billing_type=Package.BillingType.MONTHLY)
        )
        self.assertIsNone(build_comparison(monthly))


class PackagePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()
        seed_packages()

    def setUp(self):
        self.response = self.client.get(reverse("packages:list"))

    def test_page_renders_the_comparison_and_the_faq(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "table--compare")
        self.assertContains(self.response, "What changes as you move up")
        self.assertContains(self.response, "Is advertising spend included in the price?")

    def test_prices_are_published_as_structured_data(self):
        """The pricing page is the money page; the numbers have to be readable."""
        body = self.response.content.decode()
        self.assertIn("OfferCatalog", body)
        self.assertIn('"price": "15000"', body)
        self.assertIn('"price": "45000"', body)
        self.assertIn("FAQPage", body)

    def test_the_one_time_price_is_published_as_a_minimum_not_a_fixed_price(self):
        """It is shown as "from KES 30,000", so it must not claim to be exact."""
        self.assertContains(self.response, '"minPrice": "30000"')

    def test_no_struck_through_reference_price_is_shown(self):
        """Owner decision, 2026-09-17: a discount that never ends is not a discount."""
        self.assertNotContains(self.response, "package__was")
