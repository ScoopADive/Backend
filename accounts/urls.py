
from django.urls import path, include
from .views import GoogleLoginView, GoogleCallbackView

app_name = "accounts"

urlpatterns = [
    path('google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google_callback'),

]
