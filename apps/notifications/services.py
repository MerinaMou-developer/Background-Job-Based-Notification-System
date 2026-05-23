from django.db import transaction
from django.utils import timezone

from .tasks import send_notification


def enqueue_notification(notification):
    """Queue Celery task after DB commit."""
    if notification.scheduled_time <= timezone.now():
        eta = None  # run immediately
    else:
        eta = notification.scheduled_time

    transaction.on_commit(
        lambda: send_notification.apply_async(
            args=[notification.id],
            eta=eta,
        )
    )