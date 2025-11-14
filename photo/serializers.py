# photos/serializers.py
from rest_framework import serializers
from .models import Photo

class PhotoSerializer(serializers.ModelSerializer):

    image_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = Photo
        fields = '__all__'
