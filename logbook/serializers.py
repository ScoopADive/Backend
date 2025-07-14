from logbook.models import Logbook
from rest_framework import serializers


class LogbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logbook
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
