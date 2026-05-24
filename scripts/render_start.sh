#!/bin/sh
set -e

python manage.py migrate --noinput

# Render free tier has no Background Worker — run Celery beside Gunicorn in one container.
celery -A config worker -l info --concurrency 1 &

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120
