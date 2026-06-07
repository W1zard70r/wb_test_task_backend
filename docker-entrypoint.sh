#!/bin/sh
set -e

if [ "$DATABASE_URL" ]; then
  echo "Waiting for database..."
  until nc -z db 5432; do
    sleep 1
  done
fi

mkdir -p /app/logs

python manage.py migrate --noinput
python manage.py ensure_demo_admin
python manage.py runserver 0.0.0.0:8000
