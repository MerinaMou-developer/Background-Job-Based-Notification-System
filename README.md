# Background Job Based Notification System

A per-user notification API built with **Django** and **Django REST Framework**. Authenticated users schedule email notifications for a future time; **Celery** workers deliver them at the scheduled moment, with bounded retries and clear status tracking in **PostgreSQL**.

**Repository:** [MerinaMou-developer/Background-Job-Based-Notification-System](https://github.com/MerinaMou-developer/Background-Job-Based-Notification-System)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [What You Need](#what-you-need)
- [Quick Start (Docker)](#quick-start-docker-recommended)
- [Local Setup (without Docker)](#local-setup-without-docker)
- [Environment Variables](#environment-variables)
- [Running Workers & Monitoring](#running-workers--monitoring)
- [API Reference](#api-reference)
- [Business Rules](#business-rules)
- [Testing with Postman](#testing-with-postman)
- [Useful Commands](#useful-commands)

---

## Features

| Area | Description |
|------|-------------|
| **JWT authentication** | Register, login, refresh, and profile (`/api/v1/auth/`) |
| **Schedule notifications** | Title, message, and future `scheduled_time` (BDT-aware validation) |
| **Background delivery** | Celery task runs at `scheduled_time` via Redis broker |
| **Email** | SMTP delivery (Gmail App Password in local `.env`) |
| **History** | List and detail views scoped to the authenticated user |
| **Manual retry** | Retry failed jobs when `retry_count < 3` |
| **Failure handling** | After 3 failures → `permanently_failed` |
| **Docker Compose** | Web, PostgreSQL, Redis, Celery worker, and Flower |
| **Monitoring** | Flower UI for task inspection (bonus) |

---

## Architecture

```text
 Client (Postman / Browser)
        │
        ▼ JWT
 ┌──────────────┐     ┌─────────────┐
 │  Django API  │────▶│ PostgreSQL  │
 │  (DRF)       │     │ notifications│
 └──────┬───────┘     └─────────────┘
        │ enqueue (eta = scheduled_time)
        ▼
 ┌──────────────┐     ┌─────────────┐
 │    Redis     │◀───▶│ Celery      │
 │   (broker)   │     │ Worker      │
 └──────────────┘     └──────┬──────┘
                             │ SMTP
                             ▼
                        Email inbox

 Flower ── monitors Celery tasks (port 5555)
```

Optional diagram: add `docs/architecture.png` and link it here if you export one from draw.io.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | Django 5.x, Django REST Framework |
| Auth | JWT (`djangorestframework-simplejwt`) |
| Database | PostgreSQL 15 |
| Task queue | Celery 5.x |
| Broker / backend | Redis 7 |
| Email | Django SMTP backend |
| Timezone | `Asia/Dhaka` (BDT) |
| Containers | Docker, Docker Compose |
| Monitoring | Flower |

---

## Project Structure

```text
├── apps/
│   ├── users/                 # Custom user (email login), JWT views
│   ├── notifications/         # Model, APIs, Celery tasks, enqueue service
│   └── common/                # email.py, datetime_utils.py (BDT helpers)
├── config/
│   ├── settings/              # base, development, production, testing
│   ├── celery.py
│   └── urls.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── manage.py
```

---

## What You Need

### For Docker (recommended for reviewers)

| Requirement | Notes |
|-------------|--------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Running on Windows / macOS / Linux |
| `.env` file | Copy from `.env.example`; set Gmail SMTP for real email delivery |
| Gmail App Password | [Google Account → App passwords](https://myaccount.google.com/apppasswords) (if using Gmail SMTP) |

### For local development

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| PostgreSQL | 15+ |
| Redis | 7+ (or Windows Redis build) |
| pip + venv | — |

> **Never commit `.env`** — it contains secrets (DB password, SMTP password, `SECRET_KEY`).

---

## Quick Start (Docker — recommended)

### 1. Clone and configure

```powershell
git clone https://github.com/MerinaMou-developer/Background-Job-Based-Notification-System.git
cd "Background-Job-Based-Notification-System"
copy .env.example .env
```

Edit `.env` — at minimum set **SMTP** variables so emails can be sent.

### 2. Start the stack

```powershell
docker compose up --build
```

On first run, `web` applies migrations automatically.

| Service | URL / port |
|---------|------------|
| API | http://127.0.0.1:8000 |
| Admin | http://127.0.0.1:8000/admin/ |
| Flower | http://127.0.0.1:5555 |
| Postgres (host) | `localhost:5433` |
| Redis (host) | `localhost:6380` |

Host ports **5433** and **6380** avoid clashes with a local Postgres/Redis install.

### 3. Run in the background (optional)

```powershell
docker compose up -d --build
docker compose ps
docker compose logs -f celery_worker
```

### 4. Stop

```powershell
docker compose down
```

Remove database volume: `docker compose down -v`

---

## Local Setup (without Docker)

### 1. Virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements/development.txt
```

### 2. PostgreSQL & Redis

- Create database `notification_db` (user/password as in `.env`).
- Start Redis (`redis-server` or your Windows Redis install).

### 3. Environment

```powershell
copy .env.example .env
```

Set `DB_HOST=localhost`, `DB_PORT=5432`, and Celery URLs to `redis://localhost:6379/0` and `/1`.

### 4. Migrate and run API

```powershell
python manage.py migrate
python manage.py runserver
```

### 5. Celery worker (separate terminal)

**Windows** (required — default pool does not work well on Windows):

```powershell
celery -A config worker -l info --pool=solo
```

**Linux / macOS:**

```bash
celery -A config worker -l info
```

### 6. Flower (optional, separate terminal)

```powershell
celery -A config flower --port=5555
```

---

## Environment Variables

Copy [`.env.example`](./.env.example) to `.env`.

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Settings module | `config.settings.development` |
| `SECRET_KEY` | Django secret | Long random string |
| `DEBUG` | Debug mode | `True` (local only) |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DB_HOST` | PostgreSQL host | `localhost` or `db` (Docker) |
| `DB_NAME` | Database name | `notification_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_PORT` | Database port | `5432` (inside Docker network) |
| `CELERY_BROKER_URL` | Redis broker | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery results | `redis://localhost:6379/1` |
| `DJANGO_TIME_ZONE` | App timezone | `Asia/Dhaka` |
| `SMTP_HOST` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP username | `you@gmail.com` |
| `SMTP_PASSWORD` | SMTP password | Gmail App Password |
| `SMTP_USE_TLS` | Use TLS | `true` |
| `EMAIL_FROM` | From address | Same as SMTP user for Gmail |

**Docker Compose** overrides `DB_HOST`, `DB_*`, and `CELERY_*` inside containers — your `.env` SMTP settings are still used for email.

---

## Running Workers & Monitoring

| Component | Purpose | Command (local) |
|-----------|---------|-----------------|
| **Celery worker** | Sends scheduled emails | `celery -A config worker -l info --pool=solo` (Windows) |
| **Flower** | Task dashboard | `celery -A config flower --port=5555` |

With Docker, `celery_worker` and `flower` services start from `docker-compose.yml`.

---

## API Reference

**Base URL:** `http://127.0.0.1:8000/api/v1/`

**Authentication:** Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

---

### Auth

#### Register

```http
POST /api/v1/auth/register/
Content-Type: application/json
```

**Body:**

```json
{
  "email": "user@example.com",
  "password": "YourSecurePass123!",
  "password_confirm": "YourSecurePass123!",
  "first_name": "Merina",
  "last_name": "Mou"
}
```

| Status | Meaning |
|--------|---------|
| `201` | User created |
| `400` | Validation error (email taken, weak password, passwords mismatch) |

---

#### Login

```http
POST /api/v1/auth/login/
Content-Type: application/json
```

**Body:**

```json
{
  "email": "user@example.com",
  "password": "YourSecurePass123!"
}
```

**Response `200`:**

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

Use `access` for subsequent requests.

---

#### Refresh token

```http
POST /api/v1/auth/refresh/
Content-Type: application/json
```

**Body:**

```json
{
  "refresh": "<refresh_token>"
}
```

---

#### Current user

```http
GET /api/v1/auth/me/
Authorization: Bearer <access_token>
```

**Response `200`:** `id`, `email`, `first_name`, `last_name`, `date_joined`

---

### Notifications

All notification endpoints require authentication. Users only see their own records.

#### Create notification

```http
POST /api/v1/notifications/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**

```json
{
  "title": "Meeting reminder",
  "message": "Your standup starts in 10 minutes.",
  "scheduled_time": "2026-05-24T15:30:00+06:00"
}
```

| Status | Meaning |
|--------|---------|
| `201` | Created and queued (Celery ETA = `scheduled_time`) |
| `400` | Past `scheduled_time` or invalid payload |
| `401` | Missing or invalid token |

`scheduled_time` must be **in the future** (validated in BDT).

---

#### List notifications

```http
GET /api/v1/notifications/
Authorization: Bearer <access_token>
```

**Response `200`:** Array of notifications (newest first).

**Fields:** `id`, `title`, `message`, `scheduled_time`, `status`, `retry_count`, `last_error`, `sent_at`, `created_at`, `updated_at`

---

#### Notification detail

```http
GET /api/v1/notifications/{id}/
Authorization: Bearer <access_token>
```

| Status | Meaning |
|--------|---------|
| `200` | Found |
| `404` | Not found or belongs to another user |

---

#### Retry failed notification

```http
POST /api/v1/notifications/{id}/retry/
Authorization: Bearer <access_token>
```

| Status | Meaning |
|--------|---------|
| `200` | Re-queued for delivery |
| `400` | Not `failed`, permanently failed, or retry limit reached |
| `404` | Not found |

Only allowed when `status` is `failed` and `retry_count < 3`.

---

### Notification status values

| Status | Description |
|--------|-------------|
| `pending` | Initial (unused on create; create sets `scheduled`) |
| `scheduled` | Waiting for Celery ETA |
| `processing` | Worker is sending email |
| `sent` | Delivered successfully |
| `failed` | Send failed; can manual retry |
| `permanently_failed` | `retry_count` reached 3 |

---

## Business Rules

| Rule | Behavior |
|------|----------|
| Past schedule | `scheduled_time` in the past → **400** on create |
| User isolation | Users only access their own notifications |
| Retry limit | Max **3** attempts; then `permanently_failed` |
| Manual retry | Only when `status == failed` and `retry_count < 3` |
| Retry schedule | If `scheduled_time` is past on retry, it is set to **now** |
| Delivery | Email sent to the **authenticated user's email** |
| Source of truth | `retry_count` in DB; no infinite Celery autoretry |

**Lifecycle:**

```text
scheduled → processing → sent
              ↘ failed → (manual retry) → scheduled → …
              ↘ permanently_failed  (retry_count ≥ 3)
```

---

## Testing with Postman

1. **Register** → `POST /api/v1/auth/register/`
2. **Login** → `POST /api/v1/auth/login/` → copy `access`
3. Set collection variable `token` = access token  
   Header: `Authorization: Bearer {{token}}`
4. **Create notification** with `scheduled_time` **1–2 minutes in the future** (BDT offset `+06:00`)
5. Wait until `scheduled_time`, then **GET** `/api/v1/notifications/` → expect `status: sent`
6. Open **Flower** (http://127.0.0.1:5555) → confirm `send_notification` task succeeded
7. Check inbox for the user's email

To test retry, temporarily break SMTP in `.env`, create a notification, wait for `failed`, fix SMTP, then `POST .../retry/`.

---

## Useful Commands

```powershell
# Django
python manage.py check
python manage.py migrate
python manage.py createsuperuser

# Docker
docker compose up --build
docker compose exec web python manage.py createsuperuser
docker compose logs web --tail 50

# Git (use your own identity)
git config user.name "Your Name"
git config user.email "you@example.com"
```

---

## Implementation checklist

- [x] Modular settings (`development` / `production` / `testing`)
- [x] Custom user model (email login) + JWT auth
- [x] Notification model, migrations, and indexes
- [x] Create, list, detail, and retry APIs
- [x] Celery + Redis scheduling with `eta`
- [x] Email delivery via SMTP
- [x] BDT timezone helpers
- [x] Bounded retries and `permanently_failed`
- [x] Docker Compose (web, db, redis, worker, flower)
- [x] Flower monitoring

---

## License

Built as a technical assessment project.
