# 베이스 이미지
FROM python:3.11-slim

# 환경 변수
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 생성
WORKDIR /scoopadive

# 시스템 패키지 업데이트 및 psycopg2 (PostgreSQL 드라이버) 의존성 설치
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean

# pip 업그레이드 및 requirements 설치
COPY requirements.txt /scoopadive/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 프로젝트 전체 복사
COPY . /scoopadive/

# 정적 파일 수집 (필요시 주석 해제)
# RUN python manage.py collectstatic --noinput

# 포트 개방
EXPOSE 8000

# 실행 명령 (Gunicorn 사용) - 'config' -> 실제 프로젝트 이름으로 변경
CMD ["gunicorn", "scoopadive.wsgi:application", "--bind", "0.0.0.0:8000"]
