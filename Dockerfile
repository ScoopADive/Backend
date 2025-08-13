FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /scoopadive

RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /scoopadive/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /scoopadive/

EXPOSE 8000

CMD ["gunicorn", "scoopadive.wsgi:application", "--bind", "0.0.0.0:8000"]
