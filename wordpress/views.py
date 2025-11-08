from urllib.parse import urlencode

import requests
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from logbook.models import Logbook
from scoopadive import settings
from .models import WordPressToken
from .serializers import WordPressTokenSerializer, LogbookPostSerializer
from utils.wordpress import upload_image

WP_CLIENT_ID = settings.WP_CLIENT_ID
WP_CLIENT_SECRET = settings.WP_CLIENT_SECRET
WP_REDIRECT_URI = settings.WP_REDIRECT_URI
WP_REDIRECT_URI_SWAGGER = settings.WP_REDIRECT_URI_SWAGGER

User = get_user_model()

# --------------------------
# 브라우저용 OAuth
# --------------------------
@api_view(['GET', 'HEAD'])
@permission_classes([permissions.AllowAny])
def wp_login(request):
    raw_token = request.GET.get("token") or request.GET.get("state", "")
    params = {
        "client_id": WP_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": WP_REDIRECT_URI,
        "scope": "global posts",
        "state": raw_token,
        "token": raw_token,
    }
    auth_url = f"https://public-api.wordpress.com/oauth2/authorize?{urlencode(params)}"
    return redirect(auth_url)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def wp_callback(request):
    code = request.GET.get("code")
    raw_token = request.GET.get("token") or request.GET.get("state")
    if not code:
        return JsonResponse({"detail": "WordPress OAuth code missing"}, status=400)

    user = None
    if raw_token:
        try:
            validated = AccessToken(raw_token)
            user_id = validated.get("user_id")
            user = User.objects.get(id=user_id)
        except Exception as e:
            print("JWT decode failed:", e)
            user = None

    if not user:
        return JsonResponse({"detail": "User not authenticated"}, status=401)

    # WordPress access_token 요청
    res = requests.post(
        "https://public-api.wordpress.com/oauth2/token",
        data={
            "client_id": WP_CLIENT_ID,
            "client_secret": WP_CLIENT_SECRET,
            "redirect_uri": WP_REDIRECT_URI,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=10
    )
    data = res.json()
    access_token = data.get("access_token")
    if not access_token:
        return JsonResponse({"detail": "WordPress returned error", "response": data}, status=400)

    # WordPress site_id 조회
    site_res = requests.get(
        "https://public-api.wordpress.com/rest/v1.1/me/sites",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    if not site_res.get("sites"):
        return JsonResponse({"detail": "WordPress site not found"}, status=400)

    # 첫 번째 사이트 기준 (필요 시 선택 UI 추가 가능)
    site = site_res["sites"][0]
    site_id = str(site["ID"])

    # DB 저장 (user + site_id 기준)
    WordPressToken.objects.update_or_create(
        user=user,
        site_id=site_id,
        defaults={"access_token": access_token, "refresh_token": data.get("refresh_token")}
    )

    html = """
    <script>
      if (window.opener) {
        window.opener.postMessage({ wordpressConnected: true }, window.location.origin);
        window.close();
      } else {
        window.location.href = '/';
      }
    </script>
    """

    return HttpResponse(html)


# Swagger용 OAuth
# --------------------------
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def wp_login_swagger(request):
    """Swagger 전용: OAuth URL 반환"""
    auth_url = (
        f"https://public-api.wordpress.com/oauth2/authorize?"
        f"client_id={WP_CLIENT_ID}&response_type=code"
        f"&redirect_uri={WP_REDIRECT_URI_SWAGGER}"
        f"&scope=global posts"
        f"&state=swagger"
    )
    return JsonResponse({"auth_url": auth_url})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def wp_callback_swagger(request):
    """Swagger 전용: 승인 코드로 access_token 반환"""
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"detail": "WordPress OAuth code missing"}, status=400)

    res = requests.post(
        "https://public-api.wordpress.com/oauth2/token",
        data={
            "client_id": WP_CLIENT_ID,
            "client_secret": WP_CLIENT_SECRET,
            "redirect_uri": WP_REDIRECT_URI_SWAGGER,
            "code": code,
            "grant_type": "authorization_code",
        }
    )
    res.raise_for_status()
    data = res.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    if not access_token:
        return JsonResponse({"detail": "WordPress token request failed"}, status=400)

    return JsonResponse({"access_token": access_token, "refresh_token": refresh_token})


# --------------------------
# WordPressToken ViewSet
# --------------------------
class WordPressTokenViewSet(viewsets.ModelViewSet):
    queryset = WordPressToken.objects.all()
    serializer_class = WordPressTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WordPressToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --------------------------
# WordPress 유틸 함수
# --------------------------
def get_wordpress_site_id(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get("https://public-api.wordpress.com/rest/v1.1/me/sites", headers=headers)

    if res.status_code != 200:
        raise ValueError(f"WordPress API error: {res.status_code} - {res.text}")

    data = res.json()
    if not data.get("sites"):
        raise ValueError("WordPress site not found")

    return data["sites"][0]["ID"]


def post_to_wordpress(access_token, title, content, media_id=None):
    site_id = get_wordpress_site_id(access_token)
    post_data = {"title": title, "content": content, "status": "publish"}
    if media_id:
        post_data["media_ids"] = [media_id]

    url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site_id}/posts/new"
    res = requests.post(url, headers={"Authorization": f"Bearer {access_token}"}, json=post_data)
    res.raise_for_status()
    return res.json().get("URL")


# --------------------------
# Logbook → WordPress 포스트
# --------------------------
class LogbookPostViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=LogbookPostSerializer)
    @action(detail=False, methods=['post'])
    def post_to_wp(self, request):
        serializer = LogbookPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logbook_id = serializer.validated_data['logbook_id']
        site_id = serializer.validated_data.get('site_id')  # 선택적으로 site_id 전달 가능

        # 유저 토큰 가져오기
        if site_id:
            token_obj = WordPressToken.objects.filter(user=request.user, site_id=site_id).first()
        else:
            token_obj = WordPressToken.objects.filter(user=request.user).first()

        if not token_obj:
            return Response({"detail": "워드프레스 계정 로그인 필요"}, status=403)

        access_token = token_obj.access_token.strip()

        logbook = get_object_or_404(Logbook, id=logbook_id, user=request.user)

        media_id = None
        if logbook.dive_image:
            media_id = upload_image(access_token, logbook.dive_image.path, logbook.dive_image.name)

        # HTML 콘텐츠 구성
        equipment_list = ', '.join(eq.name for eq in logbook.equipment.all())
        buddy_info = logbook.buddy or 'N/A'
        dive_center_name = logbook.dive_center.name if logbook.dive_center else 'N/A'
        weather_info = logbook.weather or 'N/A'
        dive_type_info = logbook.type_of_dive or 'N/A'

        content = f"""
        <h3>{logbook.dive_title}</h3>
        <ul>
          <li><b>날짜:</b> {logbook.dive_date}</li>
          <li><b>장소:</b> {logbook.dive_site}</li>
          <li><b>최대 수심:</b> {logbook.max_depth} m</li>
          <li><b>바텀타임:</b> {str(logbook.bottom_time)}</li>
          <li><b>버디:</b> {buddy_info}</li>
          <li><b>날씨:</b> {weather_info}</li>
          <li><b>다이브 타입:</b> {dive_type_info}</li>
          <li><b>장비:</b> {equipment_list}</li>
          <li><b>납 무게:</b> {logbook.weight} kg</li>
          <li><b>탱크 압력:</b> {logbook.start_pressure} → {logbook.end_pressure}</li>
          <li><b>다이브 센터:</b> {dive_center_name}</li>
        </ul>
        <p>{logbook.feeling or ''}</p>
        """

        title = logbook.dive_title  # WordPress 포스트 제목

        try:
            post_url = post_to_wordpress(access_token, title, content, media_id)
        except requests.HTTPError as e:
            return Response(
                {"detail": f"WordPress API error: {e.response.status_code} - {e.response.text}"},
                status=e.response.status_code
            )

        return Response({"wordpress_url": post_url}, status=status.HTTP_201_CREATED)
