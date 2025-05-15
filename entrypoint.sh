#!/bin/bash
set -e

cd /scoopadive

# 예: DB 마이그레이션
python manage.py migrate

# 정적 파일 수집 (필요시)
python manage.py collectstatic --noinput

# Gunicorn 실행
exec gunicorn scoopadive.wsgi:application --bind 0.0.0.0:8000
