from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from logbook.serializers import LogbookSerializer
from mypage.models import BucketList, Friend

User = get_user_model()

class BucketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BucketList
        fields = ['id', 'title']

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['user', 'friend']

class UserDetailSerializer(serializers.ModelSerializer):
    bucketlists = BucketListSerializer(many=True, read_only=True)
    logbooks = LogbookSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'country', 'date_joined', 'bucketlists', 'logbooks']
        read_only_fields = ['date_joined', 'bucketlists', 'logbooks']

    def validate_email(self, value):
        try:
            validate_email(value)  # ✅ 올바른 Django 유효성 검사 함수 사용
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
