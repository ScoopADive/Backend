from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MyPageView, BucketListViewSet, FriendsListAPIView, FriendsDetailView, ListUsersView, \
    EditProfileView

router = DefaultRouter()
router.register(r'bucketlists', BucketListViewSet, basename='bucketlists')
urlpatterns = [
    path('', include(router.urls)),
    path('', MyPageView.as_view(), name='mypage'),
    path('all/', ListUsersView.as_view(), name='mypage-all'),

    path('friends/list/', FriendsListAPIView.as_view(), name='friends'),

    path('friends/detail/<int:id>/', FriendsDetailView.as_view(), name='friends-detail'),
    path('edit_profile/<int:id>/', EditProfileView.as_view(), name='mypage-edit'),
]

