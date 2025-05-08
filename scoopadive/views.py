from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

from logbook.models import Logbook
from .serializers import GroupSerializer, UserSerializer, LogbookSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class LogbookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Logbook.objects.all().order_by('-dive_date')
    serializer_class = LogbookSerializer
    permission_classes = [permissions.IsAuthenticated]
