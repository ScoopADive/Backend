from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TopLevelMembersListAPIView, JobViewSet, TheMostVisitedSpotsAPIView

router = DefaultRouter()
router.register('jobs', JobViewSet, basename='jobs')

urlpatterns = [
    path('top_level_members', TopLevelMembersListAPIView.as_view(), name='top_level_members'),
    path('the_most_visited_spots', TheMostVisitedSpotsAPIView.as_view(), name='the_most_visited_spots'),
    path('', include(router.urls)),

]


