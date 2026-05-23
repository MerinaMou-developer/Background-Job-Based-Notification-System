import os

from .base import *

DEBUG = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")
SECRET_KEY = os.environ.get("SECRET_KEY", SECRET_KEY)
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
