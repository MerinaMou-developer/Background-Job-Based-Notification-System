import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_email(*, to, subject, message, html_message=None, fail_silently=False):
    """
    Reusable email helper for notifications, password reset, etc.

    Args:
        to: str or list[str]
        subject: str
        message: plain text body
        html_message: optional HTML body
        fail_silently: if False, raises on SMTP errors (good for Celery task)
    """
    if isinstance(to, str):
        recipients = [to]
    else:
        recipients = list(to)

    if not recipients or not recipients[0]:
        raise ValueError("Recipient email is required.")

    logger.info("Sending email to=%s subject=%s", recipients, subject)

    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        html_message=html_message,
        fail_silently=fail_silently,
    )