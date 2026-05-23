FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/production.txt requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .
RUN chmod +x scripts/render_start.sh

EXPOSE 8000

CMD ["/app/scripts/render_start.sh"]
