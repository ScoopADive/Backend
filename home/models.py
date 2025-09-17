from django.conf import settings
from django.utils import timezone
from django.db import models

class Job(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='jobs',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
