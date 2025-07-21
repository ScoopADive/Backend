from django.urls import path, include

from . import views
from rest_framework import routers

from .views import FriendLogbookAPIView

router = routers.DefaultRouter()
router.register(r'', views.LogbookViewSet, basename='logbook')
urlpatterns = [
    path('', include(router.urls)),
    path('<int:user_id>/friend_logbooks/', FriendLogbookAPIView.as_view(), name='friend_logbook'),
    path('<int:logbook_id>/comments', views.CommentAPIView.as_view(), name='comments'),
    path('<int:logbook_id>/uncomment/<comment_id>', views.UncommentAPIView.as_view(), name='comment-delete'),
]

