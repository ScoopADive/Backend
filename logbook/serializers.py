from django.contrib.auth import get_user_model
from rest_framework import serializers
from logbook.models import Logbook, Comment, Equipment, DiveCenter

User = get_user_model()

class LogbookSerializer(serializers.ModelSerializer):
    liked_by_current_user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    buddy_input = serializers.CharField(write_only=True, required=False, allow_blank=True)
    buddy = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    # write 전용
    equipment_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    # read 전용
    equipment = serializers.SlugRelatedField(
        slug_field="name",
        many=True,
        read_only=True
    )

    class Meta:
        model = Logbook
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        buddy_input = validated_data.pop('buddy_input', None)
        equipment_names = validated_data.pop('equipment', [])

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

        # Dive coords 처리
        lat = validated_data.pop('latitude', None)
        lon = validated_data.pop('longitude', None)
        if lat is not None and lon is not None:
            validated_data['dive_coords'] = [float(lat), float(lon)]

        # Logbook 생성
        logbook = Logbook.objects.create(**validated_data)

        # Equipment 처리: 문자열 → Equipment 객체
        for name in equipment_names:
            eq, _ = Equipment.objects.get_or_create(name=name)
            logbook.equipment.add(eq)

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
