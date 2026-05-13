#!/bin/bash

set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# সুপার ইউজার তৈরি
python manage.py createsuperuser --no-input || echo "Superuser already exists"