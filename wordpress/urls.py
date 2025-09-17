# myapp/urls.py
from django.urls import path, include
from .views import wp_login, wp_callback, post_logbook_to_wp
from rest_framework.routers import DefaultRouter
from .views import WordPressTokenViewSet


router = DefaultRouter()
router.register(r"wordpress-tokens", WordPressTokenViewSet, basename="wordpress-token")

urlpatterns = [
    path("", include(router.urls)),
    path("oauth/login/", wp_login, name="wp_login"),
    path("oauth/callback/", wp_callback, name="wp_callback"),
    path("logbook/<int:logbook_id>/post/", post_logbook_to_wp, name="post_logbook_to_wp"),
]
