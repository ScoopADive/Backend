from django.contrib.auth import get_user_model
from rest_framework import serializers
from logbook.models import Logbook, Comment

User = get_user_model()


class LogbookSerializer(serializers.ModelSerializer):
    liked_by_current_user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Logbook
        fields = '__all__'
        read_only_fields = ['user', 'likes']  # likes는 읽기 전용

    def get_liked_by_current_user(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False

    def get_likes_count(self, obj):
        return obj.likes.count()


class LogbookLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logbook
        fields = ('likes',)


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author_username', 'created_at']
