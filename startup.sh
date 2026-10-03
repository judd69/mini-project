#!/bin/bash
# SecureVote - Azure App Service Startup Script

set -e

echo "Starting SecureVote..."

# Install ODBC Driver 18 for Azure SQL (not pre-installed on App Service Linux)
if ! dpkg -s msodbcsql18 > /dev/null 2>&1; then
    echo "Installing ODBC Driver 18 for SQL Server..."
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
    curl -fsSL https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
    apt-get update -qq
    ACCEPT_EULA=Y apt-get install -y -qq msodbcsql18 unixodbc-dev
    echo "ODBC Driver 18 installed."
fi

export DJANGO_SETTINGS_MODULE=securevote.settings.production

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
gunicorn securevote.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile - --error-logfile -
