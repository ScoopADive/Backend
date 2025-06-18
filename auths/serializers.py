# auths/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

# 회원가입 시리얼라이저
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'country')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 추가 클레임 넣기 가능 (예: username)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # 로그인 응답에 이메일, username 추가
        data.update({
            'email': self.user.email,
            'username': self.user.username,
            'country': self.user.country,
        })
        return data
