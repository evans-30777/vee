import threading
import time
from unittest import mock

from django.conf import settings
from django.core import mail
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from apps.core.models import NewsletterSubscriber, SiteSettings
from apps.packages.models import Package

from .models import ContactSubmission

# The enquiry redirect carries the chosen service so the conversion can be
# segmented in analytics without setting a session cookie for every enquirer.
THANK_YOU_FOR_STANDARD = "/contact/thank-you/?service=standard"

VALID_PAYLOAD = {
    "name": "Jane Mwangi",
    "email": "jane@example.com",
    "phone": "0712345678",
    "service": "standard",
    "budget": "25k_45k",
    "message": "I need help with my website and Google presence.",
}


class ContactFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()

    def test_valid_submission_saves_and_redirects(self):
        response = self.client.post(reverse("contact:contact"), VALID_PAYLOAD)
        self.assertRedirects(response, THANK_YOU_FOR_STANDARD)
        submission = ContactSubmission.objects.get()
        self.assertEqual(submission.name, "Jane Mwangi")
        self.assertEqual(submission.service, "standard")

    def test_submission_sends_admin_and_acknowledgement_emails(self):
        self.client.post(reverse("contact:contact"), VALID_PAYLOAD)
        self.assertEqual(len(mail.outbox), 2)
        admin_email, ack_email = mail.outbox
        self.assertEqual(admin_email.to, ["hello@veeagency.co.ke"])
        self.assertEqual(admin_email.reply_to, ["jane@example.com"])
        self.assertEqual(ack_email.to, ["jane@example.com"])
        self.assertTrue(ContactSubmission.objects.get().notification_sent)

    def test_enquiry_survives_email_failure(self):
        """Email is best-effort; the database record is the real lead."""
        with mock.patch(
            "apps.contact.services.get_connection", side_effect=OSError("SMTP down")
        ):
            response = self.client.post(reverse("contact:contact"), VALID_PAYLOAD)

        self.assertRedirects(response, THANK_YOU_FOR_STANDARD)
        submission = ContactSubmission.objects.get()
        self.assertFalse(submission.notification_sent)

    def test_email_timeout_is_bounded(self):
        """An unbounded SMTP socket is what turns a slow mail host into a 502."""
        self.assertTrue(settings.EMAIL_TIMEOUT)
        self.assertLessEqual(settings.EMAIL_TIMEOUT, 30)

    def test_invalid_submission_preserves_entered_values(self):
        payload = {**VALID_PAYLOAD, "email": "not-an-email"}
        response = self.client.post(reverse("contact:contact"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactSubmission.objects.count(), 0)
        self.assertContains(response, "Jane Mwangi")

    def test_a_failed_submit_gets_a_focusable_error_summary(self):
        """Without it the page reloads at the hero and nothing says why."""
        response = self.client.post(
            reverse("contact:contact"),
            {**VALID_PAYLOAD, "name": "", "email": "nope", "message": ""},
        )
        self.assertContains(response, "data-error-summary")
        self.assertContains(response, "3 things need fixing")
        self.assertContains(response, 'role="alert"')
        # Each entry jumps straight to the field it is about.
        self.assertContains(response, 'href="#id_name"')
        self.assertContains(response, 'href="#id_email"')
        self.assertContains(response, 'href="#id_message"')

    def test_one_error_is_phrased_as_one(self):
        response = self.client.post(
            reverse("contact:contact"), {**VALID_PAYLOAD, "email": "nope"}
        )
        self.assertContains(response, "One thing needs fixing")

    def test_the_browser_is_allowed_to_validate_the_form(self):
        """`novalidate` removed a free instant check and bought a round trip."""
        response = self.client.get(reverse("contact:contact"))
        self.assertNotContains(response, "novalidate")
        self.assertContains(response, "data-validate")

    def test_a_valid_submission_shows_no_summary(self):
        response = self.client.post(reverse("contact:contact"), VALID_PAYLOAD)
        self.assertEqual(response.status_code, 302)

    def test_honeypot_blocks_bot_submission(self):
        payload = {**VALID_PAYLOAD, "website": "http://spam.example.com"}
        response = self.client.post(reverse("contact:contact"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactSubmission.objects.count(), 0)

    @override_settings(CONTACT_RATE_LIMIT_PER_HOUR=2)
    def test_rate_limit_blocks_repeat_submissions(self):
        for _ in range(2):
            self.client.post(reverse("contact:contact"), VALID_PAYLOAD)
        self.assertEqual(ContactSubmission.objects.count(), 2)

        response = self.client.post(reverse("contact:contact"), VALID_PAYLOAD)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactSubmission.objects.count(), 2)

    def test_choose_plan_prefills_known_service(self):
        response = self.client.get(reverse("contact:contact") + "?service=premium")
        self.assertEqual(response.context["form"].initial.get("service"), "premium")

    def test_unknown_service_query_value_is_ignored(self):
        response = self.client.get(reverse("contact:contact") + "?service=<script>evil")
        self.assertIsNone(response.context["form"].initial.get("service"))


class NewsletterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()

    def test_subscribe_creates_subscriber(self):
        response = self.client.post(
            reverse("contact:newsletter_subscribe"),
            {"email": "reader@example.com", "source": "home"},
        )
        self.assertEqual(response.status_code, 302)
        subscriber = NewsletterSubscriber.objects.get()
        self.assertEqual(subscriber.email, "reader@example.com")
        self.assertEqual(subscriber.source, "home")

    def test_duplicate_subscription_is_handled_gracefully(self):
        for _ in range(2):
            response = self.client.post(
                reverse("contact:newsletter_subscribe"), {"email": "reader@example.com"}
            )
            self.assertEqual(response.status_code, 302)
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)

    def test_ajax_subscription_returns_json(self):
        response = self.client.post(
            reverse("contact:newsletter_subscribe"),
            {"email": "reader@example.com"},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_invalid_email_is_rejected(self):
        self.client.post(reverse("contact:newsletter_subscribe"), {"email": "nope"})
        self.assertEqual(NewsletterSubscriber.objects.count(), 0)


class AsyncEnquiryDeliveryTests(TransactionTestCase):
    """The production path, where mail is handed to a thread.

    TransactionTestCase rather than TestCase because the sending thread opens
    its own database connection: wrapped in a test transaction it would see an
    empty database, which is a property of the harness, not of the code.
    """

    def setUp(self):
        SiteSettings.objects.create()

    @override_settings(EMAIL_SEND_ASYNC=True)
    def test_response_does_not_wait_for_smtp_but_mail_still_goes_out(self):
        response = self.client.post(reverse("contact:contact"), VALID_PAYLOAD)
        self.assertRedirects(response, THANK_YOU_FOR_STANDARD)
        self.assertEqual(ContactSubmission.objects.count(), 1)

        self._join_sending_threads()

        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue(ContactSubmission.objects.get().notification_sent)

    @override_settings(EMAIL_SEND_ASYNC=True)
    def test_enquiry_survives_a_failing_mail_host_on_the_thread(self):
        with mock.patch(
            "apps.contact.services.get_connection", side_effect=OSError("SMTP down")
        ):
            response = self.client.post(reverse("contact:contact"), VALID_PAYLOAD)
            self.assertRedirects(response, THANK_YOU_FOR_STANDARD)
            self._join_sending_threads()

        submission = ContactSubmission.objects.get()
        self.assertFalse(submission.notification_sent)
        self.assertEqual(submission.name, "Jane Mwangi")

    def tearDown(self):
        # A sending thread that outlives its test would write against a
        # database the next test has already torn down.
        self._join_sending_threads(strict=False)
        super().tearDown()

    def _join_sending_threads(self, strict=True):
        deadline = time.time() + 10
        while time.time() < deadline:
            threads = [
                thread for thread in threading.enumerate()
                if thread.name.startswith("enquiry-mail-")
            ]
            if not threads:
                return
            for thread in threads:
                thread.join(timeout=deadline - time.time())
            if strict:
                for thread in threads:
                    self.assertFalse(thread.is_alive(), "enquiry mail thread did not finish")
                return
        if strict:
            self.fail("enquiry mail thread did not finish")


class ThankYouPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()

    def test_conversion_marker_carries_the_service(self):
        response = self.client.get(reverse("contact:thank_you"), {"service": "premium"})
        self.assertContains(response, '"service": "premium"')
        self.assertContains(response, '"name": "generate_lead"')

    def test_unknown_service_is_not_echoed_into_the_page(self):
        """The value reaches analytics, and the URL is user-controlled."""
        response = self.client.get(
            reverse("contact:thank_you"), {"service": "<script>alert(1)</script>"}
        )
        self.assertNotContains(response, "alert(1)")
        self.assertContains(response, '"service": ""')

    def test_thank_you_is_never_indexed(self):
        response = self.client.get(reverse("contact:thank_you"))
        self.assertContains(response, "noindex")


class EnquiryContextTests(TestCase):
    """Arriving from a priced choice should not land on a generic form."""

    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create()
        Package.objects.create(
            slug="premium", name="Premium Growth", price=45000,
            billing_type=Package.BillingType.MONTHLY,
            short_description="The full system.",
        )
        Package.objects.create(
            slug="website", name="Website Development", price=30000,
            price_is_from=True, billing_type=Package.BillingType.ONE_TIME,
        )

    def test_choosing_a_plan_names_it_back_on_the_contact_page(self):
        response = self.client.get(reverse("contact:contact"), {"service": "premium"})
        self.assertContains(response, "You're enquiring about")
        self.assertContains(response, "Premium Growth")
        self.assertContains(response, "45,000")

    def test_a_from_price_is_still_shown_as_a_starting_point(self):
        response = self.client.get(reverse("contact:contact"), {"service": "website"})
        self.assertContains(response, "from KES")

    def test_an_unknown_plan_falls_back_to_the_normal_page(self):
        response = self.client.get(reverse("contact:contact"), {"service": "nonsense"})
        self.assertNotContains(response, "You're enquiring about")
        self.assertContains(response, "holding you back")

    def test_a_website_type_prefills_the_message_and_the_service(self):
        response = self.client.get(reverse("contact:contact"), {"type": "ecommerce"})
        self.assertContains(response, "e-commerce website")
        self.assertContains(response, "Website Development")

    def test_an_unknown_website_type_is_ignored(self):
        response = self.client.get(
            reverse("contact:contact"), {"type": "<script>alert(1)</script>"}
        )
        self.assertNotContains(response, "alert(1)")
        self.assertContains(response, "holding you back")
