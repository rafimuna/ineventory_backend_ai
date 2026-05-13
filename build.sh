#!/bin/bash

set -o errexit
set -o pipefail

echo "============================================"
echo "🚀 Starting build process"
echo "============================================"

# ডিপেন্ডেন্সি ইনস্টল
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# স্ট্যাটিক ফাইল
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# মাইগ্রেশন
echo "🗄️ Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# সুপার ইউজার তৈরি - এনভায়রনমেন্ট ভেরিয়েবল চেক করে
echo "👤 Checking for superuser creation..."

# ডিবাগ তথ্য দেখুন (এনভায়রনমেন্ট ভেরিয়েবল সেট আছে কিনা)
echo "DJANGO_SUPERUSER_USERNAME is set: ${DJANGO_SUPERUSER_USERNAME:+yes}"
echo "DJANGO_SUPERUSER_PASSWORD is set: ${DJANGO_SUPERUSER_PASSWORD:+yes}"

if [[ -n "${DJANGO_SUPERUSER_USERNAME}" ]] && [[ -n "${DJANGO_SUPERUSER_PASSWORD}" ]]; then
    echo "Creating superuser: ${DJANGO_SUPERUSER_USERNAME}"
    
    # Python কোড দিয়ে সুপার ইউজার তৈরি (সবচেয়ে নির্ভরযোগ্য)
    python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superuser '{username}' created successfully")
else:
    print(f"ℹ️ Superuser '{username}' already exists")
EOF
else
    echo "⚠️ Superuser creation skipped - missing environment variables"
fi

echo "============================================"
echo "✅ Build completed successfully"
echo "============================================"