from django.db import models

# Create your models here.
from django.db import models

class Photo(models.Model):
    title = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500)  # S3 업로드된 URL 저장
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
