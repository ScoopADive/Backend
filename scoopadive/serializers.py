from django.contrib.auth.models import Group, User
from rest_framework import serializers

from logbook.models import Logbook


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class LogbookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Logbook
        fields = ['dive_image','feeling','buddy','dive_title','dive_site','dive_date','max_depth',
                  'bottom_time','weather','type_of_dive','equipment','weight','start_pressure',
                  'end_pressure','dive_center']
