import os

import dj_database_url

from .base import *

DEBUG = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")
SECRET_KEY = os.environ.get("SECRET_KEY", SECRET_KEY)

_hosts = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(",") if h.strip()]

render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_host and render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_host)

_csrf = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf.split(",") if o.strip()]
if render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_host}")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

database_url = os.environ.get("DATABASE_URL")
if database_url:
    DATABASES["default"] = dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        ssl_require=True,
    )
