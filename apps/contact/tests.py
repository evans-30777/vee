from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.models import NewsletterSubscriber, SiteSettings

from .models import ContactSubmission

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
        self.assertRedirects(response, reverse("contact:thank_you"))
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

        self.assertRedirects(response, reverse("contact:thank_you"))
        submission = ContactSubmission.objects.get()
        self.assertFalse(submission.notification_sent)

    def test_invalid_submission_preserves_entered_values(self):
        payload = {**VALID_PAYLOAD, "email": "not-an-email"}
        response = self.client.post(reverse("contact:contact"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactSubmission.objects.count(), 0)
        self.assertContains(response, "Jane Mwangi")

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
