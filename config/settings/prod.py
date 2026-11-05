import os

from .base import *  # noqa: F403,F405

DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Mailer
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "HOST": os.environ.get("EMAIL_HOST", ""),
        "PORT": int(os.environ.get("EMAIL_PORT", 587)),
        "USERNAME": os.environ.get("EMAIL_HOST_USER", ""),
        "PASSWORD": os.environ.get("EMAIL_HOST_PASSWORD", ""),
        "USE_TLS": os.environ.get("EMAIL_USE_TLS", "True") == "True",
    },
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_DB_PORT"],
    }
}
