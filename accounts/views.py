from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from auths.models import User
from pathlib import Path
import os
import json
import requests


def get_secret(setting, secrets_file='secrets.json'):
    # 1️⃣ 환경변수에서 먼저 찾기
    env_value = os.getenv(setting.upper())
    if env_value:
        return env_value

    # 2️⃣ 없으면 secrets.json 파일에서 찾기
    base_dir = Path(__file__).resolve().parent.parent
    secret_path = os.path.join(base_dir, secrets_file)
    with open(secret_path) as f:
        secrets = json.load(f)
    try:
        return secrets['web'][setting]
    except KeyError:
        raise Exception(f"Set the {setting} environment variable in {secrets_file} or as env var")

GOOGLE_CLIENT_ID = get_secret("client_id")
GOOGLE_SECRET = get_secret("client_secret")
GOOGLE_REDIRECT = get_secret("auth_uri")
GOOGLE_CALLBACK_URI = get_secret("redirect_uris")[0]


class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
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
