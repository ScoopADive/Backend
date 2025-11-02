from django.urls import path
from rest_framework.routers import DefaultRouter

from mypage.views import GetMyProfileView
from settings.views import PreferencesViewSet

router = DefaultRouter()
router.register('preferences', PreferencesViewSet, basename='preferences')

urlpatterns = [
    path('profile/', GetMyProfileView.as_view(), name='mypage_profile'),
]