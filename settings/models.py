from django.db import models
from scoopadive import settings

User = settings.AUTH_USER_MODEL

# Create your models here.
class Preferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    residence = models.CharField(max_length=20, null=True, blank=True)
    budget_min = models.CharField(max_length=30, null=True, blank=True)
    budget_max = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    preferred_depth_range = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hobbies = models.CharField(max_length=100, null=True, blank=True)
    preferred_activities = models.CharField(max_length=100, null=True, blank=True)
    preferred_atmosphere = models.CharField(max_length=100, null=True, blank=True)
    last_dive_date = models.DateField(null=True, blank=True)
    preferred_diving = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username