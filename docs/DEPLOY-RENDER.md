# Deploy on Render

Render runs **one Docker container per service** (not full `docker-compose`). You need:

| Render resource | Purpose |
|-----------------|---------|
| **PostgreSQL** | Database |
| **Redis** | Celery broker |
| **Web Service** (Docker) | Django API (Gunicorn) |
| **Background Worker** (Docker) | Celery `send_notification` |

Optional: use [`render.yaml`](../render.yaml) → **New → Blueprint** for all services at once.

---

## Step 1 — Push latest code to GitHub

Commit production Docker + settings, then push `main`.

---

## Step 2 — PostgreSQL

1. Render Dashboard → **New +** → **PostgreSQL**
2. Name: `notification-db` · Region: same as web · **Free** (if available)
3. After create, copy **Internal Database URL** (`postgres://...`)

---

## Step 3 — Redis

1. **New +** → **Redis** (or **Key Value** if shown)
2. Name: `notification-redis`
3. Copy **Internal Redis URL** → use for both:
   - `CELERY_BROKER_URL`
   - `CELERY_RESULT_BACKEND`  
   (broker `.../0` and backend `.../1` — append `/0` and `/1` to the base URL if Render gives one URL without DB index)

Example:

```text
CELERY_BROKER_URL=redis://red-xxx:6379/0
CELERY_RESULT_BACKEND=redis://red-xxx:6379/1
```

**Alternative:** [Upstash Redis](https://upstash.com/) free tier → paste URL in env vars.

---

## Step 4 — Web Service (your screenshot)

1. **New +** → **Web Service** → connect GitHub repo
2. **Language:** Docker (auto-detected)
3. **Branch:** `main`
4. **Instance type:** Free (spins down when idle — first request may be slow)

### Environment variables (Web)

| Key | Value |
|-----|--------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | long random string (generate) |
| `DEBUG` | `false` |
| `DATABASE_URL` | Internal URL from Step 2 |
| `CELERY_BROKER_URL` | Redis URL `/0` |
| `CELERY_RESULT_BACKEND` | Redis URL `/1` |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | your Gmail |
| `SMTP_PASSWORD` | Gmail App Password |
| `SMTP_USE_TLS` | `true` |
| `EMAIL_FROM` | same as SMTP user |
| `DJANGO_TIME_ZONE` | `Asia/Dhaka` |

Render auto-sets `RENDER_EXTERNAL_HOSTNAME` and `PORT` — production settings use them.

5. Click **Deploy Web Service**

After deploy, open `https://<your-app>.onrender.com/admin/` to confirm.

---

## Step 5 — Celery Background Worker

Notifications **will not send** without a worker.

1. **New +** → **Background Worker**
2. Same repo + branch
3. **Runtime:** Docker
4. **Docker Command:**

```text
celery -A config worker -l info --concurrency 2
```

5. Copy **the same env vars** as the web service (especially `DATABASE_URL`, `CELERY_*`, `SMTP_*`, `SECRET_KEY`, `DJANGO_SETTINGS_MODULE`).
6. Deploy.

---

## Step 6 — Test production API

```text
POST https://<your-app>.onrender.com/api/v1/auth/register/
POST https://<your-app>.onrender.com/api/v1/auth/login/
POST https://<your-app>.onrender.com/api/v1/notifications/
  Authorization: Bearer <access>
```

Use a future `scheduled_time`. Check worker logs on Render for `Notification X sent`.

---

## Free tier notes

- Web service **sleeps** after ~15 min idle — cold start 30–60s.
- Free PostgreSQL on Render may **expire** after 90 days — check Render docs.
- If Redis/Worker free plan is unavailable, use Upstash Redis + paid worker or document local Docker for reviewers.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `DisallowedHost` | Redeploy; ensure `RENDER_EXTERNAL_HOSTNAME` is set (automatic on Render) |
| 502 on first hit | Free tier waking up — wait and retry |
| Tasks never run | Background Worker not deployed or wrong `CELERY_BROKER_URL` |
| Email fails | Gmail App Password; allow less secure app not used — use App Password |
| Build fails | Check Render build logs; ensure `scripts/render_start.sh` is executable in repo |
