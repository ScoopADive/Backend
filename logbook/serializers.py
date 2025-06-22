from logbook.models import Logbook
from rest_framework import serializers


class LogbookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Logbook
        fields = ['user', 'dive_image','feeling','buddy','dive_title','dive_site','dive_date','max_depth',
                  'bottom_time','weather','type_of_dive','equipment','weight','start_pressure',
                  'end_pressure','dive_center']
