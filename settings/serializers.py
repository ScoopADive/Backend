from rest_framework import serializers

from settings.models import Preferences


class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_anonymous:
            raise serializers.ValidationError("Authentication required")
        validated_data['user'] = user
        return super().create(validated_data)
