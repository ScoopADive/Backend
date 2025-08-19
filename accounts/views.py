import requests
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
from auths.models import User
from scoopadive.settings import GOOGLE_REDIRECT, GOOGLE_CLIENT_ID, GOOGLE_CALLBACK_URI, GOOGLE_SECRET


FRONTEND_URL = "https://scoopadive.com"  # 메인 페이지 URL

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # 구글 로그인 페이지로 바로 redirect
        auth_url = (
            f"{GOOGLE_REDIRECT}?response_type=code"
            f"&client_id={GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_CALLBACK_URI}"
            f"&scope=email%20profile%20openid"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        return redirect(auth_url)


class GoogleCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return redirect(f"{FRONTEND_URL}/login?error=auth_code_missing")

        # 1️⃣ 구글 토큰 요청
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_SECRET,
            "redirect_uri": GOOGLE_CALLBACK_URI,
            "grant_type": "authorization_code",
        }
        token_req = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        if token_req.status_code != 200:
            return redirect(f"{FRONTEND_URL}/login?error=token_request_failed")

        access_token = token_req.json().get("access_token")
        if not access_token:
            return redirect(f"{FRONTEND_URL}/login?error=no_access_token")

        # 2️⃣ 구글 유저 정보 가져오기
        user_info_req = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"access_token": access_token},
        )
        if user_info_req.status_code != 200:
            return redirect(f"{FRONTEND_URL}/login?error=userinfo_request_failed")

        user_info = user_info_req.json()
        email = user_info.get("email")
        username = user_info.get("name") or email.split("@")[0]
        uid = user_info.get("id")
        if not email:
            return redirect(f"{FRONTEND_URL}/login?error=no_email")

        # 3️⃣ User 생성
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"username": username, "is_active": True}
        )

        # 4️⃣ SocialAccount 연결
        SocialAccount.objects.get_or_create(
            provider="google",
            uid=uid,
            defaults={"user": user, "extra_data": user_info}
        )

        # 5️⃣ JWT 발급
        refresh = RefreshToken.for_user(user)
        access_token_str = str(refresh.access_token)

        # 6️⃣ 프론트로 redirect (JWT + 사용자 정보 포함)
        frontend_redirect_url = (
            f"{FRONTEND_URL}/oauth2/redirect?"
            f"token={access_token_str}"
            f"&email={email}"
            f"&name={username}"
            f"&id={user.id}"
        )
        return redirect(frontend_redirect_url)
