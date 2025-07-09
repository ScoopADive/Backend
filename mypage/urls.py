from django.urls import path

from .models import Friend
from .views import MyPageView, BucketListDetailView, EditUserView, FriendsListAPIView, FriendsDetailView, ListUsersView

urlpatterns = [
    path('', MyPageView.as_view(), name='mypage'),
    path('all/', ListUsersView.as_view(), name='mypage-all'),
    path('bucketlist/<int:id>/', BucketListDetailView.as_view({'get': 'retrieve'}), name='bucketlist-detail'),
    path('friends/list/', FriendsListAPIView.as_view(), name='friends'),

    path('friends/detail/<int:id>/', FriendsDetailView.as_view(), name='friends-detail'),
    path('edit_profile/<int:id>/', EditUserView.as_view(), name='mypage-edit'),
]

