from django.urls import path, include

from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'', views.LogbookViewSet, basename='logbook')

# router.register(r'likes', views.LogbookLikesViewSet, basename='logbook-likes')

urlpatterns = [
    path('', include(router.urls)),

    # path('likes/<int:id>', views.LogbookLikesAPIView.as_view(), name='logbook-likes'),
]

