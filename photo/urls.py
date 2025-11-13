from django.urls import include, path
from rest_framework.routers import DefaultRouter

from photo.views import PhotoViewSet

router = DefaultRouter()
router.register(r'', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls)),
]