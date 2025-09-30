from django.db import models

from scoopadive import settings

User = settings.AUTH_USER_MODEL

class Preferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    residence = models.CharField(max_length=20, null=True, blank=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    preferred_depth_range = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hobbies = models.CharField(max_length=100, null=True, blank=True)
    preferred_activities = models.CharField(max_length=100, null=True, blank=True)
    preferred_atmosphere = models.CharField(max_length=100, null=True, blank=True)
    last_dive_date = models.DateField(null=True, blank=True)
    preferred_diving = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username


class BucketList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bucketlists')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Friend(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey(User, related_name='friend_of', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')  # 중복 친구 관계 방지
        indexes = [
            models.Index(fields=['user', 'friend']),
        ]

    def __str__(self):
        return f"{self.user} is friends with {self.friend}"


class SkillSet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skill_sets')
    skill = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


