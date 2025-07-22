from django.db import models
from auths.models import User

# Create your models here.
class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()