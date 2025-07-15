from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TopLevelMembersList, JobViewSet

router = DefaultRouter()
router.register('jobs', JobViewSet, basename='jobs')

urlpatterns = [
    path('top_level_members', TopLevelMembersList.as_view(), name='top_level_members'),
    path('', include(router.urls)),
]


