from django.contrib.auth import get_user_model
from rest_framework import serializers
from logbook.models import Logbook, Comment, Equipment

User = get_user_model()

class LogbookSerializer(serializers.ModelSerializer):
    # Likes 관련
    liked_by_current_user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    # Buddy 처리
    buddy_input = serializers.CharField(write_only=True, required=False, allow_blank=True)
    buddy = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    # Equipment write용
    equipment_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    # Equipment read용
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
        # write-only 필드 pop
        buddy_input = validated_data.pop('buddy_input', '')

        # 멘션 처리
        buddy_user = None
        buddy_str = ''
        if buddy_input.startswith('@'):
            username = buddy_input[1:].strip()
            try:
                buddy_user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                raise serializers.ValidationError({'buddy_input': 'User not found'})
        else:
            buddy_str = buddy_input

        validated_data['buddy'] = buddy_user  # FK용
        validated_data['buddy_str'] = buddy_str  # 문자열용

        # Dive coords 처리
        lat = validated_data.pop('latitude', None)
        lon = validated_data.pop('longitude', None)
        if lat is not None and lon is not None:
            validated_data['dive_coords'] = [float(lat), float(lon)]

        # Logbook 생성 (equipment 제외)
        logbook = Logbook.objects.create(**validated_data)

        # Equipment 처리 (옵션)
        equipment_list = validated_data.pop('equipment_names', [])
        for eq_name in equipment_list:
            eq_obj, _ = Equipment.objects.get_or_create(name=eq_name)
            logbook.equipment.add(eq_obj)

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
