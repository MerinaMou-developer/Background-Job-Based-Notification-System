import logging

from celery import shared_task
from django.utils import timezone

from apps.common.datetime_utils import format_bdt
from apps.common.email import send_email

from .models import Notification

logger = logging.getLogger(__name__)
MAX_RETRIES = 3


@shared_task
def send_notification(notification_id):
    try:
        notification = Notification.objects.select_related("user").get(pk=notification_id)
    except Notification.DoesNotExist:
        logger.warning("Notification %s not found", notification_id)
        return

    if notification.status in (
        Notification.Status.SENT,
        Notification.Status.PERMANENTLY_FAILED,
        Notification.Status.PROCESSING,
    ):
        return

    notification.status = Notification.Status.PROCESSING
    notification.save(update_fields=["status", "updated_at"])

    try:
        send_email(
            to=notification.user.email,
            subject=notification.title,
            message=notification.message,
            fail_silently=False,
        )

        notification.status = Notification.Status.SENT
        notification.sent_at = timezone.now()
        notification.last_error = ""
        notification.save(
            update_fields=["status", "sent_at", "last_error", "updated_at"]
        )
        logger.info(
            "Notification %s sent at %s",
            notification.id,
            format_bdt(notification.sent_at),
        )

    except Exception as exc:
        notification.retry_count += 1
        notification.last_error = str(exc)[:2000]

        if notification.retry_count >= MAX_RETRIES:
            notification.status = Notification.Status.PERMANENTLY_FAILED
        else:
            notification.status = Notification.Status.FAILED

        notification.save(
            update_fields=["status", "retry_count", "last_error", "updated_at"]
        )
        logger.exception(
            "Notification %s failed (attempt %s)",
            notification.id,
            notification.retry_count,
        )