from logbook.models import Comment
from rest_framework import serializers
from .models import Logbook, Equipment

class LogbookSerializer(serializers.ModelSerializer):
    liked_by_current_user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dive_image_url = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = Logbook
        fields = '__all__'
        read_only_fields = ('user', 'likes')

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        # equipment 직접 꺼내기
        equipment_names = self.initial_data.get("equipment", [])
        if not isinstance(equipment_names, list):
            equipment_names = []

        logbook = super().create(validated_data)

        for name in equipment_names:
            eq, _ = Equipment.objects.get_or_create(name=name)
            logbook.equipment.add(eq)

        return logbook

    def update(self, instance, validated_data):
        equipment_names = self.initial_data.get("equipment", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if isinstance(equipment_names, list):
            instance.equipment.clear()
            for name in equipment_names:
                eq, _ = Equipment.objects.get_or_create(name=name)
                instance.equipment.add(eq)

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # equipment를 문자열 배열로 변환
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
