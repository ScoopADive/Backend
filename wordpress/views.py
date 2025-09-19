import requests
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import WordPressToken
from .serializers import WordPressTokenSerializer, LogbookPostSerializer
from logbook.models import Logbook
from utils.wordpress import upload_image
from django.conf import settings

WP_CLIENT_ID = settings.WP_CLIENT_ID
WP_CLIENT_SECRET = settings.WP_CLIENT_SECRET
WP_REDIRECT_URI = settings.WP_REDIRECT_URI
WP_REDIRECT_URI_SWAGGER = settings.WP_REDIRECT_URI_SWAGGER


# --------------------------
# 브라우저용 WordPress OAuth
# --------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wp_login(request):
    """브라우저용: OAuth 승인 페이지로 리다이렉트"""
    auth_url = (
        f"https://public-api.wordpress.com/oauth2/authorize?"
        f"client_id={WP_CLIENT_ID}&response_type=code"
        f"&redirect_uri={WP_REDIRECT_URI}"
    )
    return redirect(auth_url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wp_callback(request):
    """브라우저용: OAuth 콜백 처리 후 DB 저장"""
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"detail": "WordPress OAuth code missing"}, status=400)

    res = requests.post(
        "https://public-api.wordpress.com/oauth2/token",
        data={
            "client_id": WP_CLIENT_ID,
            "client_secret": WP_CLIENT_SECRET,
            "redirect_uri": WP_REDIRECT_URI,
            "code": code,
            "grant_type": "authorization_code",
        }
    ).json()

    access_token = res.get("access_token")
    refresh_token = res.get("refresh_token")
    if not access_token:
        return JsonResponse({"detail": "WordPress token request failed"}, status=400)

    WordPressToken.objects.update_or_create(
        user=request.user,
        defaults={"access_token": access_token, "refresh_token": refresh_token}
    )

    return redirect("https://scoopadive.com/home")


# --------------------------
# Swagger용 WordPress OAuth
# --------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def wp_login_swagger(request):
    """Swagger 전용: JWT 없이 OAuth URL 확인"""
    auth_url = (
        f"https://public-api.wordpress.com/oauth2/authorize?"
        f"client_id={WP_CLIENT_ID}&response_type=code"
        f"&redirect_uri={WP_REDIRECT_URI_SWAGGER}"
        f"&state=swagger"
    )
    return JsonResponse({"auth_url": auth_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def wp_callback_swagger(request):
    """Swagger용: 승인 코드로 WordPress 토큰 발급만"""
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
    ).json()

    access_token = res.get("access_token")
    refresh_token = res.get("refresh_token")
    if not access_token:
        return JsonResponse({"detail": "WordPress token request failed"}, status=400)

    return JsonResponse({
        "access_token": access_token,
        "refresh_token": refresh_token
    })


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
# WordPress 포스트 업로드 함수
# --------------------------
def post_to_wordpress(access_token, title, content, media_id=None):
    # 연결된 사이트 ID 확인
    site_res = requests.get(
        "https://public-api.wordpress.com/rest/v1.1/me/sites",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    if not site_res.get("sites"):
        raise ValueError("WordPress site not found")

    site_id = site_res["sites"][0]["ID"]  # 첫 번째 사이트 선택

    post_data = {
        "title": title,
        "content": content,
        "status": "publish"
    }

    if media_id:
        post_data["media_ids"] = [media_id]

    url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site_id}/posts/new"

    res = requests.post(url, headers={"Authorization": f"Bearer {access_token}"}, data=post_data)
    res.raise_for_status()
    return res.json().get("URL")


# --------------------------
# Logbook → WordPress 포스트
# --------------------------
class LogbookPostViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    @swagger_auto_schema(request_body=LogbookPostSerializer)
    def post_to_wp(self, request):
        serializer = LogbookPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logbook_id = serializer.validated_data['logbook_id']

        try:
            token_obj = WordPressToken.objects.get(user=request.user)
        except WordPressToken.DoesNotExist:
            return Response(
                {"detail": "워드프레스 계정으로 로그인 후 사용하세요."},
                status=status.HTTP_403_FORBIDDEN
            )

        logbook = get_object_or_404(Logbook, id=logbook_id, user=request.user)

        media_id = None
        if logbook.dive_image:
            media_id = upload_image(
                token_obj.access_token,
                logbook.dive_image.path,
                logbook.dive_image.name
            )

        title = logbook.dive_title
        content = f"""
        <h3>{logbook.dive_title}</h3>
        <ul>
          <li><b>날짜:</b> {logbook.dive_date}</li>
          <li><b>장소:</b> {logbook.dive_site}</li>
          <li><b>최대 수심:</b> {logbook.max_depth} m</li>
          <li><b>바텀타임:</b> {logbook.bottom_time}</li>
          <li><b>버디:</b> {logbook.buddy}</li>
          <li><b>날씨:</b> {logbook.weather}</li>
          <li><b>다이브 타입:</b> {logbook.type_of_dive}</li>
          <li><b>장비:</b> {', '.join(eq.name for eq in logbook.equipment.all())}</li>
          <li><b>납 무게:</b> {logbook.weight} kg</li>
          <li><b>탱크 압력:</b> {logbook.start_pressure} → {logbook.end_pressure}</li>
          <li><b>다이브 센터:</b> {logbook.dive_center}</li>
        </ul>
        <p>{logbook.feeling}</p>
        """

        post_url = post_to_wordpress(token_obj.access_token, title, content, media_id)

        return Response(
            {"wordpress_url": post_url},
            status=status.HTTP_201_CREATED
        )
