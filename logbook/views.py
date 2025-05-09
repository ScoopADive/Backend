from rest_framework import permissions, viewsets

from logbook.models import Logbook
from .serializers import LogbookSerializer


class LogbookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Logbook.objects.all().order_by('-dive_date')
    serializer_class = LogbookSerializer
    permission_classes = [permissions.IsAuthenticated]
