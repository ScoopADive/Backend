from django.db import models
from scoopadive import settings

User = settings.AUTH_USER_MODEL

# Create your models here.
class BucketList(models.Model):
    user = models.ForeignKey(User, related_name='bucketlists', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Friend(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_of', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')  # 중복 친구 관계 방지
        indexes = [
            models.Index(fields=['user', 'friend']),
        ]

    def __str__(self):
        return f"{self.user} is friends with {self.friend}"
