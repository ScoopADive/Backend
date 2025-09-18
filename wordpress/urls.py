# myapp/urls.py
from django.urls import path, include
from .views import wp_login, wp_callback, wp_login_swagger, wp_callback_swagger
from rest_framework.routers import DefaultRouter
from .views import WordPressTokenViewSet, LogbookPostViewSet

router = DefaultRouter()
router.register(r"wordpress-tokens", WordPressTokenViewSet, basename="wordpress-token")
router.register(r"logbook-post", LogbookPostViewSet, basename="logbook-post")

urlpatterns = [
    path("oauth/login/", wp_login, name="wp_login"),
    path("oauth/callback/", wp_callback, name="wp_callback"),

    path("oauth/login/swagger/", wp_login_swagger, name="wp_login_swagger"),
    path("oauth/callback/swagger/", wp_callback_swagger, name="wp_callback_swagger"),

    path("", include(router.urls)),
]
