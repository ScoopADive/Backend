FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /scoopadive

# -----------------------------
# 시스템 패키지 설치
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    locales \
 && rm -rf /var/lib/apt/lists/*

# -----------------------------
# UTF-8 locale 설정
# -----------------------------
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
 && locale-gen

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# -----------------------------
COPY requirements.txt /scoopadive/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /scoopadive/

EXPOSE 8000

CMD ["gunicorn", "scoopadive.wsgi:application", "--bind", "0.0.0.0:8000"]
