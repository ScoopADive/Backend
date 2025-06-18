# auths/urls.py
from django.urls import path
from .views import UserSignupView, CustomTokenObtainPairView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "auths"
urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('signin/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
