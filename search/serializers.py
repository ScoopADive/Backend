from rest_framework import serializers
from auths.models import User
from home.models import Job
from logbook.models import Logbook, Comment
from mypage.models import BucketList, Friend


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'country', 'license', 'introduction', 'profile_image']


class LogbookSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logbook
        fields = [
            'id',
            'dive_title',
            'dive_site',
            'feeling',
            'dive_date',
            'max_depth',
            'bottom_time',
            'weather',
            'type_of_dive',
            'weight',
            'start_pressure',
            'end_pressure',
        ]


class CommentSearchSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at', 'author_username']


class BucketListSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BucketList
        fields = ['id', 'title', 'created_at']


class FriendSearchSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    friend_username = serializers.CharField(source='friend.username', read_only=True)

    class Meta:
        model = Friend
        fields = ['id', 'user_username', 'friend_username', 'created_at']


class JobSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'location', 'description']
