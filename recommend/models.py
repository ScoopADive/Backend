from django.db import models
from auths.models import User

class Spot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    region = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    intro = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.region




