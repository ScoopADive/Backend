from django.urls import path

from .models import Friend
from .views import MyPageView, BucketListDetailView, FriendDetailView, EditUserView

urlpatterns = [
    path('', MyPageView.as_view(), name='mypage'),
    path('bucketlist/<int:pk>/', BucketListDetailView.as_view({'get': 'retrieve'}), name='bucketlist-detail'),
    path('friend/<int:pk>/', FriendDetailView.as_view({'get': 'retrieve'}), name='friend-detail'),
    path('edit_profile/<int:pk>/', EditUserView.as_view(), name='mypage-edit'),
]

