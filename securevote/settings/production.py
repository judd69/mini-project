"""
SecureVote — Production settings (Azure App Service).
Activate with: DJANGO_SETTINGS_MODULE=securevote.settings.production
"""
import os
from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = [
    os.environ.get('WEBSITE_HOSTNAME', 'localhost'),
    '.azurewebsites.net',
]

# ── Database ──────────────────────────────────────────────────────────
# SQLite on Azure persistent storage (/home survives restarts).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/db.sqlite3',
    }
}

# ── Security Hardening ────────────────────────────────────────────────
# NOTE: Do NOT set SECURE_SSL_REDIRECT = True on Azure App Service.
# Azure's load balancer handles HTTPS termination and the internal
# warmup probe hits http://localhost:8000 — if we redirect that to
# HTTPS, Azure never gets a 200 and the container times out.
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    'https://*.azurewebsites.net',
    f"https://{os.environ.get('WEBSITE_HOSTNAME', 'localhost')}",
]

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# ── Logging ───────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
