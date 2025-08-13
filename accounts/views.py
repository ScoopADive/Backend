from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from auths.models import User
import os
import requests

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        GOOGLE_CLIENT_ID = os.environ.get("CLIENT_ID")
        GOOGLE_SECRET = os.environ.get("CLIENT_SECRET")
        GOOGLE_REDIRECT = os.environ.get("AUTH_URI")
        GOOGLE_CALLBACK_URI = os.environ.get("REDIRECT_URIS")

        auth_url = (
            f"{GOOGLE_REDIRECT}?response_type=code"
            f"&client_id={GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_CALLBACK_URI}"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        return Response({"auth_url": auth_url})


class GoogleCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST)

        GOOGLE_CLIENT_ID = os.environ.get("CLIENT_ID")
        GOOGLE_SECRET = os.environ.get("CLIENT_SECRET")
        GOOGLE_REDIRECT = os.environ.get("AUTH_URI")
        GOOGLE_CALLBACK_URI = os.environ.get("REDIRECT_URIS")

        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_SECRET,
            "redirect_uri": GOOGLE_CALLBACK_URI,
            "grant_type": "authorization_code",
        }

        token_req = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        if token_req.status_code != 200:
            return Response({"error": "Failed to get access token"}, status=status.HTTP_400_BAD_REQUEST)

        token_req_json = token_req.json()
        access_token = token_req_json.get("access_token")
        if not access_token:
            return Response({"error": "Access token not found in response"}, status=status.HTTP_400_BAD_REQUEST)

        user_info_req = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"access_token": access_token},
        )
        if user_info_req.status_code != 200:
            return Response({"error": "Failed to get user info"}, status=status.HTTP_400_BAD_REQUEST)

        user_info = user_info_req.json()
        email = user_info.get("email")
        if not email:
            return Response({"error": "Email not found in user info"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User account does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            social_user = SocialAccount.objects.get(user=user)
            if social_user.provider != "google":
                return Response({"error": "User account not exist for Google login"}, status=status.HTTP_400_BAD_REQUEST)
        except SocialAccount.DoesNotExist:
            return Response({"error": "Social account not linked"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
            },
            "message": "login success",
            "token": {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }
        }, status=status.HTTP_200_OK)
