from django.urls import path, include

from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', views.LogbookViewSet, basename='logbook')
urlpatterns = [
    path('', include(router.urls)),
    path('my_logbooks', views.MyLogbooksAPIView.as_view(), name='my_logbooks'),
    path('<int:logbook_id>/comments', views.CommentAPIView.as_view(), name='comments'),
    path('<int:logbook_id>/uncomment/<comment_id>', views.UncommentAPIView.as_view(), name='comment-delete'),
]

