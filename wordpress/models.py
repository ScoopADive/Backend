# myapp/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from scoopadive import settings


class WordPressToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wordpress_tokens')
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)  # 만료 시간 관리용

    def is_expired(self):
        return self.expires_at and now() >= self.expires_at

