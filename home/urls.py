from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TopLevelMember


urlpatterns = [
    path('top_level_member', TopLevelMember.as_view(), name='top_level_member'),
]

