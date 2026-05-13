#!/bin/bash

set -o errexit

echo "🚀 Starting build process..."

# ডিপেন্ডেন্সি ইনস্টল
pip install -r requirements.txt

# স্ট্যাটিক ফাইল সংগ্রহ
python manage.py collectstatic --no-input

# ডাটাবেস মাইগ্রেশন
python manage.py migrate

# সুপার ইউজার তৈরি (DOWNLOAD 받은 Environment Variables ব্যবহার করে)
if [[ -n "$DJANGO_SUPERUSER_USERNAME" ]] && [[ -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
    echo "👤 Creating superuser from environment variables..."
    python manage.py createsuperuser --no-input || echo "ℹ️ Superuser already exists"
else
    echo "⚠️ Superuser creation skipped: missing environment variables"
fi

echo "✅ Build completed!"