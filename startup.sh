#!/bin/bash
set -e
echo "Starting SecureVote..."
export DJANGO_SETTINGS_MODULE=securevote.settings.production
echo "Running migrations..."
python manage.py migrate --noinput
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Seeding initial data..."
python manage.py shell < seed_data.py
echo "Creating superuser..."
python create_superuser.py
echo "Starting Gunicorn..."
gunicorn securevote.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile - --error-logfile -
