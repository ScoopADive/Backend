from logbook.models import Logbook, Comment
from rest_framework import serializers


class LogbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logbook
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class LogbookLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logbook
        fields = ('likes',)

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author_username', 'created_at']
