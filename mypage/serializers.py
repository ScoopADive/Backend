from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from logbook.serializers import LogbookSerializer
from mypage.models import BucketList, Friend, SkillSet, Preferences

User = get_user_model()

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = '__all__'

class BucketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BucketList
        fields = '__all__'

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserDetailSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)
    bucketlists = BucketListSerializer(many=True, read_only=True)
    own_logbooks = LogbookSerializer(many=True, read_only=True)
    friends = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'profile_image', 'email', 'username', 'country', 'introduction',
            'date_joined', 'bucketlists', 'own_logbooks', 'friends', 'license'
        ]
        read_only_fields = ['date_joined', 'bucketlists', 'own_logbooks']

    def get_friends(self, obj):
        friend_ids = Friend.objects.filter(user=obj).values_list('friend_id', flat=True)
        return list(friend_ids)


class UserUpdateSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['profile_image', 'username', 'email', 'country', 'license', 'introduction']

    def validate_email(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("유효한 이메일 주소를 입력하세요.")
        return value

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("사용자 이름은 최소 3자 이상이어야 합니다.")
        return value

    def validate_country(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("국가명은 알파벳만 포함해야 합니다.")
        return value

class SkillSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillSet
        fields = '__all__'
        read_only_fields = ['user']