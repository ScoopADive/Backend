from logbook.models import Logbook
from rest_framework import serializers


class LogbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logbook
        fields = '__all__'


