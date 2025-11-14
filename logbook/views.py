from asgiref.sync import sync_to_async
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.parsers import MultiPartParser

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView

from auths.models import User
from logbook.models import Logbook, Comment
from .serializers import LogbookSerializer, LogbookLikeSerializer, CommentSerializer


class LogbookViewSet(viewsets.ModelViewSet):
    queryset = Logbook.objects.all().order_by('-dive_date')
    parser_classes = [MultiPartParser]

    def get_serializer_class(self):
        if self.action == 'like':
            return LogbookLikeSerializer
        return LogbookSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_likes', 'get_like']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, pk=None):
        logbook = get_object_or_404(Logbook, pk=pk)
        if logbook.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        logbook.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def my_logbooks(self, request):
        logbooks = Logbook.objects.filter(user=self.request.user)
        serializer = LogbookSerializer(logbooks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def likes(self, request):
        data = [
            {
                'id': logbook.id,
                'likes': list(logbook.likes.values_list('username', flat=True))
            }
            for logbook in self.queryset if logbook.likes.exists()
        ]
        return Response(data)

    @action(detail=True, methods=['get', 'post', 'delete'])
    def like(self, request, pk=None):
        log = self.get_object()
        user = request.user

        if request.method == 'GET':
            likes = list(log.likes.values_list('username', flat=True))
            return Response({
                'likes': likes,
                'likes_count': log.likes.count()
            })

        elif request.method == 'POST':
            log.likes.add(user)
            return Response({
                'liked': True,
                'likes_count': log.likes.count()
            }, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            log.likes.remove(user)
            return Response({
                'liked': False,
                'likes_count': log.likes.count()
            }, status=status.HTTP_200_OK)


class LikesAsyncView(APIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request):
        async_get_likes = sync_to_async(
            lambda: [
                {
                    'id': logbook.id,
                    'likes': list(logbook.likes.values_list("username", flat=True))
                }
                for logbook in Logbook.objects.all().prefetch_related("likes")
            ],
            thread_sensitive=True
        )
        data = await async_get_likes()
        return Response(data)

class FriendLogbookAPIView(APIView):
    serializer_class = LogbookSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id=None):
        user = User.objects.get(id=user_id)
        logbooks = Logbook.objects.filter(user=user)
        serializer = LogbookSerializer(logbooks, many=True)
        return Response(serializer.data)

class CommentAPIView(generics.CreateAPIView):
    queryset = Comment.objects.all().order_by('created_at')
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]


    def get(self, request, logbook_id=None):
        logbook = get_object_or_404(Logbook, pk=logbook_id)
        comments = logbook.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, logbook_id=None):
        logbook = get_object_or_404(Logbook, pk=logbook_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(logbook=logbook, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, logbook_id=None):
        logbook = get_object_or_404(Logbook, pk=logbook_id)
        comment_text = request.data.get('text')
        if comment_text:
            comment = Comment.objects.create(
                logbook=logbook,
                text=comment_text,
                author=request.user
            )

class UncommentAPIView(APIView):
    queryset = Comment.objects.all().order_by('created_at')
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, logbook_id=None, comment_id=None):
        logbook = get_object_or_404(Logbook, pk=logbook_id)
        comment = logbook.comments.get(pk=comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
