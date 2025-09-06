FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /scoopadive

# 필수 빌드 도구 설치 (한 번만 실행)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /scoopadive/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /scoopadive/

EXPOSE 8000

CMD ["gunicorn", "scoopadive.wsgi:application", "--bind", "0.0.0.0:8000"]
