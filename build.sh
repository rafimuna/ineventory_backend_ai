#!/bin/bash

set -o errexit

echo "============================================"
echo "🚀 Starting build process"
echo "============================================"

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

echo "👤 Creating superuser..."
if [[ -n "$DJANGO_SUPERUSER_USERNAME" ]] && [[ -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
    python manage.py createsuperuser --no-input 2>/dev/null || echo "ℹ️ Superuser already exists"
    echo "✅ Superuser setup complete"
else
    echo "⚠️ Superuser environment variables not set"
    echo "   Add DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD"
fi

echo "============================================"
echo "✅ Build completed successfully!"
echo "============================================"