"""
WSGI config for SecureVote project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Azure sets DJANGO_SETTINGS_MODULE as an Application Setting.
# Locally it falls back to development if the var is not set.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securevote.settings.development')
application = get_wsgi_application()
