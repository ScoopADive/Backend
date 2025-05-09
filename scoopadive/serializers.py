from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login = attrs.get("username")  # 필드명은 username 그대로 유지 (프론트단 이름 바꾸기 귀찮을 수 있음)
        password = attrs.get("password")

        # 이메일 또는 사용자명으로 유저 찾기
        user = User.objects.filter(email=login).first() or User.objects.filter(username=login).first()

        if user and user.check_password(password):
            data = super().validate({'username': user.username, 'password': password})
            data['user_id'] = user.id
            data['username'] = user.username
            data['email'] = user.email
            return data

        raise serializers.ValidationError("이메일 또는 사용자명이 잘못되었거나 비밀번호가 일치하지 않습니다.")
