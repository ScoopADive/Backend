from rest_framework import permissions, viewsets, status
from rest_framework.parsers import MultiPartParser

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from logbook.models import Logbook
from .serializers import LogbookSerializer


class LogbookViewSet(viewsets.ModelViewSet):
    queryset = Logbook.objects.all().order_by('-dive_date')
    serializer_class = LogbookSerializer
    parser_classes = [MultiPartParser]  # 이미지 업로드를 위해 필요

    def get_permissions(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        logbooks = Logbook.objects.all().order_by('-dive_date')
        serializer = LogbookSerializer(logbooks, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = LogbookSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        logbook = get_object_or_404(Logbook, pk=pk)
        serializer = LogbookSerializer(logbook)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        logbook = get_object_or_404(Logbook, pk=pk)
        if logbook.user == request.user:
            logbook.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)



class LogbookLikesAllAPIView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]  # 권한 확인도 안 함

    def get(self, request):
        logbooks = Logbook.objects.all()
        logbooks_likes = [
            {
                'id': logbook.id,
                'likes': list(logbook.likes.values_list('username', flat=True))
            }
            for logbook in logbooks
            if logbook.likes.exists()
        ]
        return Response(logbooks_likes)


class LogbookLikesAPIView(APIView):
    def get_permissions(self):
        if self.request.method in ['POST', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request, id):
        logbook = get_object_or_404(Logbook, id=id)
        logbook_likes = list(logbook.likes.values_list('username', flat=True))
        return Response(logbook_likes)

    def post(self, request, id):
        logbook = get_object_or_404(Logbook, id=id)
        logbook.likes.add(request.user)
        logbook.save()
        logbook_likes = list(logbook.likes.values_list('username', flat=True))
        return Response(logbook_likes)

    def delete(self, request, id):
        logbook = get_object_or_404(Logbook, id=id)
        logbook.likes.remove(request.user)
        logbook.save()
        logbook_likes = list(logbook.likes.values_list('username', flat=True))
        return Response(logbook_likes)
