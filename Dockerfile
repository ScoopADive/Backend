FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------
# UTF-8 locale 설치/설정
# -----------------------------
RUN apt-get update || apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc libpq-dev locales \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# -----------------------------
WORKDIR /scoopadive

COPY requirements.txt /scoopadive/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /scoopadive/

EXPOSE 8000

CMD ["gunicorn", "scoopadive.wsgi:application", "--bind", "0.0.0.0:8000"]
