from django.db import models

from django.db import models

class Photo(models.Model):
    title = models.CharField(max_length=100)
    image_url = models.CharField(max_length=1000, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    classified_as = models.CharField(max_length=255, null=False, default="Unknown")

    def __str__(self):
        return self.title
