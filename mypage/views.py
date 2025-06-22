from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser

from .models import BucketList, Friend
from .serializers import UserDetailSerializer, BucketListSerializer, FriendSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

User = get_user_model()
# Create your views here.
class MyPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

class BucketListDetailView(viewsets.ModelViewSet):
    queryset = BucketList.objects.all().order_by('created_at')
    serializer_class = BucketListSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]  # 이미지 업로드를 위해 필요

    def retrieve(self, request, pk=None):
        bucketlist = get_object_or_404(BucketList, pk=pk)
        serializer = BucketListSerializer(bucketlist)
        return Response(serializer.data)

class FriendDetailView(viewsets.ModelViewSet):
    queryset = Friend.objects.all().order_by('created_at')
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def retrieve(self, request, pk=None):
        friend = get_object_or_404(Friend, pk=pk)
        serializer = FriendSerializer(friend)
        return Response(serializer.data)



class EditUserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=UserDetailSerializer)
    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if request.user != user:
            return Response({'detail': '수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        # partial=True로 하면 request.data에 없는 필드는 기존 값 유지
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
