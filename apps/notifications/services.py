import logging

from django.db import transaction
from django.utils import timezone

from .tasks import send_notification

logger = logging.getLogger(__name__)


def enqueue_notification(notification):
    """Queue Celery task after DB commit."""
    if notification.scheduled_time <= timezone.now():
        eta = None  # run immediately
    else:
        eta = notification.scheduled_time

    notification_id = notification.id

    def dispatch():
        try:
            send_notification.apply_async(
                args=[notification_id],
                eta=eta,
            )
        except Exception:
            logger.exception(
                "Failed to enqueue notification %s (check CELERY_BROKER_URL / rediss SSL)",
                notification_id,
            )
            raise

    transaction.on_commit(dispatch)