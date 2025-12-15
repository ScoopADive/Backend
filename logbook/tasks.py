from celery import shared_task
from django.core.cache import cache
from .models import Logbook

@shared_task
def add_like_task(logbook_id, user_id):
    log = Logbook.objects.get(id=logbook_id)
    log.likes.add(user_id)  # DB에 좋아요 추가
    cache.delete("logbook_likes")  # 캐시 무효화


@shared_task
def remove_like_task(logbook_id, user_id):
    log = Logbook.objects.get(id=logbook_id)
    log.likes.remove(user_id)  # DB에서 좋아요 제거
    cache.delete("logbook_likes")  # 캐시 무효화


