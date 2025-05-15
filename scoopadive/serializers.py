from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

User = get_user_model()
