# 베이스 이미지
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /scoopadive

RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean

COPY requirements.txt /scoopadive/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /scoopadive/

# entrypoint.sh 복사 및 실행권한 부여
COPY entrypoint.sh /scoopadive/entrypoint.sh
RUN chmod +x /scoopadive/entrypoint.sh

EXPOSE 8000

# ENTRYPOINT 지정
ENTRYPOINT ["/scoopadive/entrypoint.sh"]
