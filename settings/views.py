from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from settings.models import Preferences
from settings.serializers import PreferencesSerializer


# Create your views here.
class PreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = PreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Preferences.objects.filter(user=self.request.user).order_by('id')


