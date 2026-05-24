# Background Job Based Notification System

Per-user notification API: schedule an email for a future time (BDT), **Celery** delivers it in the background, with retries and status tracking in **PostgreSQL**.

**Repo:** [MerinaMou-developer/Background-Job-Based-Notification-System](https://github.com/MerinaMou-developer/Background-Job-Based-Notification-System)

**Live API:** https://background-job-based-notification-system-kex6.onrender.com/

---

## Architecture

![Notification System Architecture](./docs/architecture.png)

---

## Features

- JWT auth (register, login, refresh, profile)
- Create / list / detail notifications (per user)
- Celery + Redis — task runs at `scheduled_time`
- Email via SMTP (Gmail App Password in `.env`)
- Manual retry for failed jobs (max 3 attempts)
- Docker Compose: API, Postgres, Redis, Celery worker, Flower

**Stack:** Django 5 · DRF · PostgreSQL · Celery · Redis · Docker

---

## Run with Docker (recommended)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) running
- Copy `.env.example` → `.env` and set **SMTP** (Gmail [App Password](https://myaccount.google.com/apppasswords))

> Do not commit `.env`.

### Start

```powershell
git clone https://github.com/MerinaMou-developer/Background-Job-Based-Notification-System.git
cd "Background-Job-Based-Notification-System"
copy .env.example .env
# edit .env — SMTP_USER, SMTP_PASSWORD, EMAIL_FROM

docker compose up --build
```

| Service | URL |
|---------|-----|
| API & docs home | http://127.0.0.1:8000/ |
| API base | http://127.0.0.1:8000/api/v1/ |
| Health check | http://127.0.0.1:8000/health/ |
| Flower | http://127.0.0.1:5555 |
| Postgres (host) | `localhost:5433` |
| Redis (host) | `localhost:6380` |

Migrations run automatically on first start.

**Background:**

```powershell
docker compose up -d --build
docker compose logs -f celery_worker
```

**Stop:**

```powershell
docker compose down
```

---

## Quick test (Postman)

1. `POST /api/v1/auth/register/` — email, password, password_confirm  
2. `POST /api/v1/auth/login/` — copy `access` token  
3. Header: `Authorization: Bearer <access>`  
4. `POST /api/v1/notifications/` — set `scheduled_time` **2–3 minutes ahead** (BDT, e.g. `2026-05-24T15:30:00+06:00`)  
5. After that time → `GET /api/v1/notifications/` → `status` should be `sent` (check register email + spam)

---

## API endpoints

Base: `/api/v1/` · Auth header: `Bearer <access_token>`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | API overview page |
| GET | `/health/` | No | DB + Celery broker check |
| POST | `/auth/register/` | No | Register |
| POST | `/auth/login/` | No | JWT access + refresh |
| POST | `/auth/refresh/` | No | Refresh access token |
| GET | `/auth/me/` | Yes | Current user |
| GET | `/notifications/` | Yes | List my notifications |
| POST | `/notifications/` | Yes | Create & schedule |
| GET | `/notifications/{id}/` | Yes | Detail |
| POST | `/notifications/{id}/retry/` | Yes | Retry if `failed` |

**Create body:**

```json
{
  "title": "Meeting reminder",
  "message": "Standup in 10 minutes.",
  "scheduled_time": "2026-05-24T15:30:00+06:00"
}
```

---

## Business rules

| Rule | Behavior |
|------|----------|
| `scheduled_time` | Must be in the future (BDT) → else `400` |
| Email recipient | Logged-in user's email |
| Retries | Max 3 → then `permanently_failed` |
| Manual retry | Only when `status` is `failed` |

**Status flow:** `scheduled` → `processing` → `sent` · failures → `failed` → retry or `permanently_failed`

---

## Configuration

See [`.env.example`](./.env.example). Docker Compose overrides `DB_HOST` / `CELERY_*` inside containers; your `.env` SMTP values are used for email.

---

## Production (Render)

Deployed on Render (Neon Postgres + Upstash Redis). Celery runs in the same web container on the free tier (`scripts/render_start.sh`). First request after idle may take ~30s (cold start).

---

## License

Technical assessment project.
