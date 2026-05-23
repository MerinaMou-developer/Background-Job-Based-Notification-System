"""
Reusable timezone helpers (BDT = Asia/Dhaka, UTC+6).
Use across serializers, tasks, and services.
"""
from zoneinfo import ZoneInfo

from django.utils import timezone

BDT_ZONE_NAME = "Asia/Dhaka"
BDT_TZ = ZoneInfo(BDT_ZONE_NAME)


def get_bdt_timezone():
    """Return BDT ZoneInfo (for make_aware, astimezone, etc.)."""
    return BDT_TZ


def ensure_aware_bdt(dt):
    """
    Naive datetimes are treated as BDT.
    Aware datetimes are converted to BDT.
    """
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, BDT_TZ)
    return dt.astimezone(BDT_TZ)


def to_bdt(dt):
    """Convert any aware (or naive) datetime to BDT."""
    return ensure_aware_bdt(dt)


def to_utc(dt):
    """Convert datetime to UTC (for storage/comparison with Django now())."""
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, BDT_TZ)
    return dt.astimezone(ZoneInfo("UTC"))


def now_bdt():
    """Current time in BDT."""
    return timezone.now().astimezone(BDT_TZ)


def now_utc():
    """Current time as timezone-aware UTC."""
    return timezone.now()


def format_bdt(dt, fmt="%Y-%m-%d %H:%M:%S"):
    """Human-readable string in BDT for logs or API messages."""
    return f"{to_bdt(dt).strftime(fmt)} BDT"


def is_in_future(dt):
    """True if dt is after now (timezone-safe)."""
    aware = ensure_aware_bdt(dt) if timezone.is_naive(dt) else dt
    return aware > timezone.now()
