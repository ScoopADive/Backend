from django.db import models
from django.contrib.auth.models import User
from scoopadive import settings


class WordPressToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()
    site_id = models.CharField(max_length=255)  # WordPress 사이트 ID
    refresh_token = models.TextField(null=True, blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'site_id')
