from django.urls import path, include

from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'', views.LogbookViewSet, basename='logbook')


urlpatterns = [
    path('', include(router.urls)),
    path('likes/all/', views.LogbookLikesAllAPIView.as_view(), name='logbook-likes-all'),

    path('likes/<int:id>', views.LogbookLikesAPIView.as_view(), name='logbook-likes'),


]

