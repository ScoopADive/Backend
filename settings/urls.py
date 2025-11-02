from django.urls import include, path
from rest_framework.routers import DefaultRouter
from settings.views import PreferencesViewSet

router = DefaultRouter()
router.register('preferences', PreferencesViewSet, basename='preferences')

urlpatterns = [
    path('', include(router.urls)),
]