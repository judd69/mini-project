#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# SecureVote — Azure App Service Startup Script
# Runs on every container start in Azure App Service (Linux)
# ═══════════════════════════════════════════════════════════════════

set -e

echo "🗳️  SecureVote — Starting up..."

# Apply database migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Collect static files (WhiteNoise serves them)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "🚀 Starting Gunicorn..."
gunicorn securevote.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile '-' \
    --error-logfile '-'
