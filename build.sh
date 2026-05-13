#!/bin/bash

set -o errexit
set -o pipefail

echo "============================================"
echo "🚀 Starting build process"
echo "============================================"

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🗄️ Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "👤 Setting up superuser..."

# সুপার ইউজার তৈরির জন্য Python কোড (সরাসরি createsuperuser কমান্ডের চেয়ে বেশি নির্ভরযোগ্য)
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ Superuser '{username}' created successfully")
    else:
        print(f"ℹ️ Superuser '{username}' already exists")
else:
    print("⚠️ DJANGO_SUPERUSER_PASSWORD not set - skipping superuser creation")
EOF

echo "============================================"
echo "✅ Build completed successfully!"
echo "============================================"