#!/bin/sh

echo "Apply database migrations"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Start Gunicorn"
gunicorn scoopadive.wsgi:application --bind 0.0.0.0:8000
