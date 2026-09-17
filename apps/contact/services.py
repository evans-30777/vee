"""Enquiry side effects. The database record is the primary record of a lead."""

import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import connections
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_enquiry_notifications(submission):
    """Notify the team and acknowledge the enquirer.

    Email failure must never surface as a broken form: the enquiry is already
    saved. Failures are logged and flagged on the record instead.
    """
    from apps.core.models import SiteSettings

    delivered = False

    # Read separately: the contact details this puts in the email body are a
    # nicety, but a database hiccup while fetching them must not be the reason
    # nobody is told an enquiry arrived.
    try:
        current_settings = SiteSettings.load()
    except Exception:
        logger.exception("Could not load SiteSettings for enquiry %s", submission.pk)
        current_settings = None

    email_context = {"submission": submission, "site_settings": current_settings}
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
        try:
            submission.notification_sent = True
            submission.save(update_fields=["notification_sent", "updated_at"])
        except Exception:
            # The mail went out; only the bookkeeping failed. Off the request
            # thread there is nobody to report this to, and re-raising would
            # only surface as an unhandled thread exception.
            logger.exception(
                "Could not flag notification_sent for submission %s", submission.pk
            )

    return delivered


def _send_in_background(submission):
    try:
        send_enquiry_notifications(submission)
    finally:
        # A thread gets its own database connection and has to return it, or
        # every enquiry leaks one for the life of the process.
        connections.close_all()


def dispatch_enquiry_notifications(submission):
    """Hand the enquiry emails off without making the visitor wait for SMTP.

    Sending inline blocks the response on two SMTP round trips. If the mail
    host stalls — and EMAIL_TIMEOUT bounds that, but does not remove it — the
    request can outlive the worker timeout and the visitor sees an error page
    for an enquiry that was already saved. They assume it failed; we never
    find out. So the response goes out as soon as the row is committed.

    Kept synchronous where EMAIL_SEND_ASYNC is off (development and tests), so
    assertions about mail.outbox stay deterministic.
    """
    if not getattr(settings, "EMAIL_SEND_ASYNC", False):
        return send_enquiry_notifications(submission)

    thread = threading.Thread(
        target=_send_in_background,
        args=(submission,),
        name=f"enquiry-mail-{submission.pk}",
        daemon=True,
    )
    thread.start()
    return None
