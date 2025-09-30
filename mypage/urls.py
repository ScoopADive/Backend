from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .serializers import PreferencesSerializer
from .views import MyPageView, BucketListViewSet, FriendsListAPIView, FriendsDetailView, ListUsersView, \
    EditProfileView, MySkillsViewSet, GetMyProfileView, PreferencesViewSet

router = DefaultRouter()
router.register(r'bucketlists', BucketListViewSet, basename='bucketlists')

router.register('myskills', MySkillsViewSet, basename='myskills')

router.register('preferences', PreferencesViewSet, basename='preferences')
urlpatterns = [
    path('', include(router.urls)),

    path('profile/', GetMyProfileView.as_view(), name='mypage_profile'),

    path('', MyPageView.as_view(), name='mypage'),
    path('all/', ListUsersView.as_view(), name='mypage-all'),

    path('friends/list/', FriendsListAPIView.as_view(), name='friends'),

    path('friends/detail/<int:id>/', FriendsDetailView.as_view(), name='friends-detail'),
    path('edit_profile/<int:id>/', EditProfileView.as_view(), name='mypage-edit'),

]

