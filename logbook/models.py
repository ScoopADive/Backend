from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta

from logbook.constants import WEATHER_CHOICES, DIVE_TYPE_CHOICES


# 보조 장비/일반 장비 분리
class Equipment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DiveCenter(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class Logbook(models.Model):
    dive_image = models.ImageField(upload_to='logbooks', null=True, blank=True)
    feeling = models.TextField(null=True, blank=True)
    buddy = models.CharField(max_length=256)
    dive_title = models.CharField(max_length=256)
    dive_site = models.CharField(max_length=256)
    dive_date = models.DateField()
    max_depth = models.FloatField(null=True, blank=True)
    bottom_time = models.DurationField(help_text="예: 00:35:00 (35분)")
    weather = models.CharField(max_length=100, choices=WEATHER_CHOICES, null=True, blank=True)
    type_of_dive = models.CharField(max_length=256, choices=DIVE_TYPE_CHOICES, null=True, blank=True)
    equipment = models.ManyToManyField(Equipment, related_name="logs", blank=True)
    weight = models.PositiveSmallIntegerField(help_text="사용한 납 무게 (kg)")
    start_pressure = models.PositiveSmallIntegerField()
    end_pressure = models.PositiveSmallIntegerField()
    dive_center = models.ForeignKey(DiveCenter, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-dive_date']

    def clean(self):
        if self.end_pressure > self.start_pressure:
            raise ValidationError("End pressure cannot be greater than start pressure.")
        if self.bottom_time and self.bottom_time < timedelta(minutes=1):
            raise ValidationError("Bottom time must be at least 1 minute.")

    def __str__(self):
        return f"{self.dive_title} @ {self.dive_site} ({self.dive_date})"
