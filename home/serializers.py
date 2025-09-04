from rest_framework import serializers
from home.models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['user', 'created_at']  # created_at 읽기 전용 추가

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
