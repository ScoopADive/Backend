from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser

from .models import BucketList, Friend
from .serializers import UserDetailSerializer, BucketListSerializer, FriendSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
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

class ListUsersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()
        serializer = UserDetailSerializer(users, many=True)
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

class FriendsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        friends = User.objects.filter(friend_of__user=user).distinct()
        serializer = UserDetailSerializer(friends, many=True)
        return Response(serializer.data)


class FriendsDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user = request.user
        friend = user.friends.get(id=id)
        return Response(friend)

    def post(self, request, id):
        user = request.user
        friend = get_object_or_404(User, id=id)

        print(f"Adding user with id: {user.id} to friend: {friend}")
        print(f"Adding friend with id: {friend.id}")

        if user == friend:
            return Response({'error': '자기 자신을 친구로 추가할 수 없습니다.'}, status=400)

        # 이미 친구인지 확인
        if Friend.objects.filter(user=user, friend=friend).exists():
            return Response({'error': '이미 친구입니다.'}, status=400)

        # 친구 관계 추가
        Friend.objects.create(user=user, friend=friend)
        Friend.objects.create(user=friend, friend=user)  # 양방향 관계

        return Response({'message': '친구 추가 성공'}, status=201)


    def delete(self, request, id):
        user = request.user
        friend = get_object_or_404(User, id=id)

        if user == friend:
            return Response({'error': '자기 자신은 삭제할 수 없습니다.'}, status=400)

        # 친구 관계 삭제 (양방향)
        Friend.objects.filter(user=user, friend=friend).delete()
        Friend.objects.filter(user=friend, friend=user).delete()

        return Response({'message': '친구 삭제 완료'}, status=status.HTTP_204_NO_CONTENT)


# class FriendDetailView(viewsets.ModelViewSet):
#     queryset = Friend.objects.all().order_by('created_at')
#     serializer_class = FriendSerializer
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser]
#
#     def retrieve(self, request, pk=None):
#         friend = get_object_or_404(Friend, pk=pk)
#         serializer = FriendSerializer(friend)
#         return Response(serializer.data)



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
