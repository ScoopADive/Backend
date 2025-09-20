from django.db import models
from django.contrib.auth.models import User
from scoopadive import settings


class WordPressToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user',)  # 사용자별 하나만 존재

