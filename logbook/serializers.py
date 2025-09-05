from django.contrib.auth import get_user_model
from rest_framework import serializers
from logbook.models import Logbook, Comment, Equipment, DiveCenter

User = get_user_model()


class LogbookSerializer(serializers.ModelSerializer):
    liked_by_current_user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    buddy_input = serializers.CharField(write_only=True, required=False, allow_blank=True)
    buddy = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    equipment_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Logbook
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        buddy_input = validated_data.pop('buddy_input', None)
        equipment_ids = validated_data.pop('equipment_ids', [])

        # Buddy 처리
        if buddy_input and buddy_input.startswith('@'):
            username = buddy_input[1:].strip()
            try:
                user = User.objects.get(username__iexact=username)
                validated_data['buddy'] = user
                validated_data['buddy_str'] = ''
            except User.DoesNotExist:
                raise serializers.ValidationError({'buddy_input': 'User not found'})
        else:
            validated_data['buddy'] = None
            validated_data['buddy_str'] = buddy_input or ''

        # Logbook 생성
        logbook = Logbook.objects.create(**validated_data)

        # Equipment 연결
        if equipment_ids:
            equipment_objs = Equipment.objects.filter(id__in=equipment_ids)
            logbook.equipment.set(equipment_objs)

        return logbook

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
