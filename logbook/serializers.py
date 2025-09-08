from logbook.models import Comment
# serializers.py
from rest_framework import serializers
from .models import Logbook, Equipment

class LogbookSerializer(serializers.ModelSerializer):
    liked_by_current_user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    # equipment를 문자열 리스트로 받도록 설정
    equipment = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Logbook
        fields = '__all__'
        read_only_fields = ('user', 'likes')

    def create(self, validated_data):
        # 사용자 정보 자동 설정
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        # equipment 문자열 리스트 꺼내기
        equipment_names = validated_data.pop("equipment", [])
        logbook = super().create(validated_data)

        # 장비 이름으로 Equipment 연결 (없으면 생성)
        for name in equipment_names:
            eq, _ = Equipment.objects.get_or_create(name=name)
            logbook.equipment.add(eq)

        return logbook

    def update(self, instance, validated_data):
        # equipment 문자열 리스트 꺼내기
        equipment_names = validated_data.pop("equipment", None)

        # 다른 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # equipment 업데이트
        if equipment_names is not None:
            instance.equipment.clear()
            for name in equipment_names:
                eq, _ = Equipment.objects.get_or_create(name=name)
                instance.equipment.add(eq)

        return instance

    def to_representation(self, instance):
        """Response에서 equipment를 문자열 배열로 반환"""
        rep = super().to_representation(instance)
        rep['equipment'] = [eq.name for eq in instance.equipment.all()]
        return rep

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
        read_only_fields = ('likes',)  # 직접 수정 금지


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author_username', 'created_at']
