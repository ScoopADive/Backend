from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model

from logbook.models import Logbook, Comment
from mypage.models import BucketList, Friend
from search.serializers import UserSearchSerializer, LogbookSearchSerializer, CommentSearchSerializer, \
    BucketListSearchSerializer, FriendSearchSerializer, JobSearchSerializer

User = get_user_model()

class GlobalSearchAPIView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="검색어",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request):
        q = request.GET.get('q', '').strip()
        if not q:
            return Response({'error': '검색어(q)를 입력하세요.'}, status=400)

        users = User.objects.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(country__icontains=q) |
            Q(license__icontains=q) |
            Q(introduction__icontains=q)
        )

        logbooks = Logbook.objects.filter(
            Q(dive_title__icontains=q) |
            Q(dive_site__icontains=q) |
            Q(feeling__icontains=q)
        )

        comments = Comment.objects.filter(
            Q(text__icontains=q)
        )

        bucketlists = BucketList.objects.filter(
            Q(title__icontains=q)
        )

        friends = Friend.objects.filter(
            Q(user__username__icontains=q) |
            Q(friend__username__icontains=q)
        )

        from home.models import Job
        jobs = Job.objects.filter(
            Q(title__icontains=q) |
            Q(location__icontains=q) |
            Q(description__icontains=q)
        )

        return Response({
            "users": UserSearchSerializer(users, many=True).data,
            "logbooks": LogbookSearchSerializer(logbooks, many=True).data,
            "comments": CommentSearchSerializer(comments, many=True).data,
            "bucketlists": BucketListSearchSerializer(bucketlists, many=True).data,
            "friends": FriendSearchSerializer(friends, many=True).data,
            "jobs": JobSearchSerializer(jobs, many=True).data,
        })
