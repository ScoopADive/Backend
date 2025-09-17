# myapp/serializers.py
from rest_framework import serializers
from .models import WordPressToken

class WordPressTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordPressToken
        fields = ["id", "user", "access_token", "refresh_token", "expires_at"]
        read_only_fields = ["user"]  # user는 자동 연결되도록

class LogbookPostSerializer(serializers.Serializer):
    logbook_id = serializers.IntegerField()
