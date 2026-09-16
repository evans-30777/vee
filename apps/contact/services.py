"""Enquiry side effects. The database record is the primary record of a lead."""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_enquiry_notifications(submission):
    """Notify the team and acknowledge the enquirer.

    Email failure must never surface as a broken form: the enquiry is already
    saved. Failures are logged and flagged on the record instead.
    """
    from apps.core.models import SiteSettings

    delivered = False
    email_context = {"submission": submission, "site_settings": SiteSettings.load()}
    try:
        connection = get_connection(fail_silently=False)
        admin_message = EmailMultiAlternatives(
            subject=f"New enquiry from {submission.name}",
            body=render_to_string("contact/emails/admin_notification.txt", email_context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ENQUIRY_NOTIFICATION_EMAIL],
            reply_to=[submission.email],
            connection=connection,
        )
        admin_message.send()

        acknowledgement = EmailMultiAlternatives(
            subject="We've received your enquiry — VEE Agency",
            body=render_to_string("contact/emails/enquiry_ack.txt", email_context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[submission.email],
            connection=connection,
        )
        acknowledgement.send()
        delivered = True
    except Exception:
        logger.exception("Enquiry email delivery failed for submission %s", submission.pk)

    if delivered and not submission.notification_sent:
        submission.notification_sent = True
        submission.save(update_fields=["notification_sent", "updated_at"])

    return delivered
