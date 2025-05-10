from django.contrib.auth.models import Group, User
from rest_framework import viewsets

from logbook.models import Logbook
from .serializers import GroupSerializer

from rest_framework import permissions


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


