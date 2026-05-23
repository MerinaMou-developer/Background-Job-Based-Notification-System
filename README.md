# Notification System

A background job–based notification API built with **Django** and **Django REST Framework**. Users authenticate, schedule notifications for a future time, and track delivery status—with bounded retries and permanent failure after repeated errors.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Business Rules](#business-rules)
- [API Reference](#api-reference)
- [Development](#development)
- [Roadmap](#roadmap)

---

## Overview

This service accepts notification requests over HTTP, persists them in **PostgreSQL**, and dispatches delivery through **Celery** workers backed by **Redis**. Scheduling, retries, and status transitions are stored in the database so the system remains observable and safe under failure.

The codebase follows a modular layout: split settings per environment, domain apps under `apps/`, and infrastructure defined for **Docker Compose** (web, database, broker, workers).

---

## Features

| Area | Description |
|------|-------------|
| **Authentication** | JWT-based API access (register / login) |
| **Create notification** | Title, message, and scheduled delivery time |
| **Schedule delivery** | Background task runs at `scheduled_time` |
| **History** | Paginated list of a user's notifications |
| **Retry** | Manual retry for failed jobs; automatic retries capped at 3 |
| **Validation** | Requests with `scheduled_time` in the past are rejected (`400`) |
| **Failure handling** | After 3 failures → `permanently_failed` (no infinite retries) |

---

## Architecture

High-level request flow: client → authenticated API → validation → database → Celery (ETA) → worker → status update.

![Notification System Architecture](./docs/architecture.png)

<details>
<summary><strong>Flow summary</strong></summary>

1. **Client** sends an HTTP request with a JWT.
2. **DRF** authenticates the user and routes to the appropriate view.
3. **Serializer** validates payload; rejects past `scheduled_time`.
4. **PostgreSQL** stores the notification record.
5. **Celery** enqueues `send_notification` with `eta=scheduled_time`.
6. **Worker** executes at the scheduled time, updates status, and applies retry rules.
7. **Retry API** allows manual retry only when status and `retry_count` permit it.

</details>

> **Diagram file:** Save your draw.io export as [`docs/architecture.png`](./docs/architecture.png).  
> If your file is still named `Untitled Diagram.drawio.png`, rename it to `architecture.png` so the link above works on GitHub.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | Django 5.x, Django REST Framework |
| Auth | JWT (djangorestframework-simplejwt) |
| Database | PostgreSQL |
| Task queue | Celery |
| Message broker | Redis |
| Containers | Docker, Docker Compose |
| Monitoring (bonus) | Flower |

---

## Project Structure

```text
notification-system/
├── apps/
│   ├── users/              # Authentication & user domain
│   └── notifications/      # Notification model, APIs, tasks
├── config/
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── development.py  # Local development
│   │   ├── production.py   # Production overrides
│   │   └── testing.py      # Test runner settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── docs/
│   └── architecture.png    # System architecture diagram
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── static/
├── media/
├── templates/
├── tests/
├── manage.py
├── .env.example
└── docker-compose.yml      # (planned)
```

---

## Prerequisites

- Python 3.11+ (3.12 recommended)
- pip & virtualenv
- PostgreSQL 15+ (local or via Docker)
- Redis 7+ (when Celery is enabled)
- Docker & Docker Compose (optional, for full stack)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/notification-system.git
cd notification-system
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements/development.txt
```

> Until requirement files are populated, install manually:  
> `pip install django djangorestframework`

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your local values (see [Environment Variables](#environment-variables)).

### 5. Apply migrations & run the server

```bash
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

### 6. Verify the project

```bash
python manage.py check
```

---

## Environment Variables

Copy [`.env.example`](./.env.example) to `.env` and set:

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Settings module for the environment | `config.settings.development` |
| `SECRET_KEY` | Django secret key | *(generate a unique value)* |
| `DEBUG` | Debug mode (`True` only locally) | `True` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@localhost:5432/notifications` |
| `CELERY_BROKER_URL` | Redis broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379/1` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |

Never commit `.env` to version control.

---

## Business Rules

These rules are enforced in serializers, services, and Celery tasks:

| Rule | Behavior |
|------|----------|
| Past schedule | If `scheduled_time` &lt; now → **400 Bad Request** |
| Retry limit | Max **3** attempts; then status → `permanently_failed` |
| Manual retry | Only when status is `failed` and `retry_count` &lt; 3 |
| User isolation | Users can only access their own notifications |
| Source of truth | `retry_count` in the database controls retries (not unbounded Celery autoretry) |

### Notification status lifecycle

```text
pending → scheduled → processing → sent
                              ↘ failed → (retry) → processing
                              ↘ permanently_failed  (retry_count ≥ 3)
```

### Notification fields

| Field | Type | Notes |
|-------|------|-------|
| `title` | string | Short summary |
| `message` | text | Body content |
| `scheduled_time` | datetime (UTC) | Must be in the future on create |
| `status` | enum | See lifecycle above |
| `retry_count` | integer | Incremented on each failed attempt |

---

## API Reference

> **Documentation in progress.** Endpoints will be documented here once implemented.

Base URL: `/api/v1/`

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `POST` | `/auth/register/` | Register a new user | Planned |
| `POST` | `/auth/login/` | Obtain JWT access & refresh tokens | Planned |
| `POST` | `/notifications/` | Create & schedule a notification | Planned |
| `GET` | `/notifications/` | List notification history (paginated) | Planned |
| `GET` | `/notifications/{id}/` | Retrieve a single notification | Planned |
| `POST` | `/notifications/{id}/retry/` | Retry a failed notification | Planned |

Example requests, response schemas, and error codes will be added in a follow-up section.

---

## Development

### Settings modules

| Environment | Module |
|-------------|--------|
| Local | `config.settings.development` |
| Production | `config.settings.production` |
| Tests | `config.settings.testing` |

`manage.py` defaults to **development** settings.

### Useful commands

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py test
```

### Docker (planned)

```bash
docker compose up --build
```

Services: `web`, `db` (PostgreSQL), `redis`, `celery_worker`, `celery_beat`, `flower`.

---

## Roadmap

- [x] Project scaffold & modular settings
- [x] `users` and `notifications` apps
- [ ] User authentication (JWT)
- [ ] Notification model & migrations
- [ ] CRUD / schedule / history APIs
- [ ] Celery tasks & retry logic
- [ ] Docker Compose
- [ ] API documentation in this README
- [ ] Tests for validation, retries, and permissions

---

## License

This project was built as a technical assessment. License TBD.
