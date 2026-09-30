"""
SecureVote — Production settings (Azure SQL, DEBUG=False).
Activate with: DJANGO_SETTINGS_MODULE=securevote.settings.production
"""
import os
import dj_database_url
from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = [
    os.environ.get('WEBSITE_HOSTNAME', 'localhost'),
    '.azurewebsites.net',
]

# ── Database ──────────────────────────────────────────────────────────
# Reads DATABASE_URL from Azure App Service configuration.
# Fallback to SQLite if not set (shouldn't happen in production).
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        ssl_require=True,
    )
}

# ── Security Hardening ────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000   # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
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
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
