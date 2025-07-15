from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser

from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from logbook.models import Logbook
from .serializers import LogbookSerializer, LogbookLikeSerializer


class LogbookViewSet(viewsets.ModelViewSet):
    queryset = Logbook.objects.all().order_by('-dive_date')
    parser_classes = [MultiPartParser]

    def get_serializer_class(self):
        if self.action == 'like':
            return LogbookLikeSerializer
        return LogbookSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'like', 'unlike']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def destroy(self, request, pk=None):
        logbook = get_object_or_404(Logbook, pk=pk)
        if logbook.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        logbook.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def get_likes(self, request):
        data = [
            {
                'id': logbook.id,
                'likes': list(logbook.likes.values_list('username', flat=True))
            }
            for logbook in self.queryset if logbook.likes.exists()
        ]
        return Response(data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def get_like(self, request, pk=None):
        logbook = get_object_or_404(Logbook, pk=pk)
        likes = list(logbook.likes.values_list('username', flat=True))
        return Response(likes)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        logbook = self.get_object()
        logbook.likes.add(request.user)
        return Response({'status': f'Liked logbook {pk}'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        logbook = self.get_object()
        logbook.likes.remove(request.user)
        return Response({'status': f'Unliked logbook {pk}'}, status=status.HTTP_204_NO_CONTENT)
