from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta

from logbook.constants import WEATHER_CHOICES, DIVE_TYPE_CHOICES
from scoopadive import settings

User = settings.AUTH_USER_MODEL

class Equipment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DiveCenter(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class Logbook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='own_logbooks')
    dive_image = models.ImageField(upload_to='logbooks_images', null=True, blank=True)
    feeling = models.TextField(null=True, blank=True)
    buddy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buddy_logbooks')
    # buddy = models.TextField(null=True, blank=True)
    dive_title = models.CharField(max_length=256)
    dive_site = models.CharField(max_length=256)
    dive_date = models.DateField()
    max_depth = models.FloatField()
    bottom_time = models.DurationField(help_text="예: 00:35:00 (35분)")
    weather = models.CharField(max_length=100, choices=WEATHER_CHOICES, null=True, blank=True)
    type_of_dive = models.CharField(max_length=256, choices=DIVE_TYPE_CHOICES, null=True, blank=True)
    equipment = models.ManyToManyField(Equipment, related_name="equipment", blank=True)
    weight = models.PositiveSmallIntegerField(help_text="사용한 납 무게 (kg)")
    start_pressure = models.PositiveSmallIntegerField()
    end_pressure = models.PositiveSmallIntegerField()
    dive_center = models.ForeignKey(DiveCenter, on_delete=models.SET_NULL, null=True, blank=True)
    likes = models.ManyToManyField(User, related_name="liked_logbooks", blank=True)

    def total_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ['-dive_date']

    def clean(self):
        if self.end_pressure > self.start_pressure:
            raise ValidationError("End pressure cannot be greater than start pressure.")
        if self.bottom_time and self.bottom_time < timedelta(minutes=1):
            raise ValidationError("Bottom time must be at least 1 minute.")

    def __str__(self):
        return f"{self.dive_title} @ {self.dive_site} ({self.dive_date})"

class Comment(models.Model):
    logbook = models.ForeignKey(Logbook, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.logbook} @ {self.user}"