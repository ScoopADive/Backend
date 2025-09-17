from django.contrib.sites import requests
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import WordPressToken
from .serializers import WordPressTokenSerializer, LogbookPostSerializer
from logbook.models import Logbook
from utils.wordpress import upload_image, post_to_wordpress

WP_CLIENT_ID = settings.WP_CLIENT_ID
WP_CLIENT_SECRET = settings.WP_CLIENT_SECRET
WP_REDIRECT_URI = settings.WP_REDIRECT_URI


# --------------------------
# WordPress OAuth
# --------------------------
@login_required
def wp_login(request):
    auth_url = (
        f"https://public-api.wordpress.com/oauth2/authorize?"
        f"client_id={WP_CLIENT_ID}&response_type=code&redirect_uri={WP_REDIRECT_URI}"
    )
    return redirect(auth_url)


@login_required
def wp_callback(request):
    code = request.GET.get("code")
    token_url = "https://public-api.wordpress.com/oauth2/token"
    res = requests.post(token_url, data={
        "client_id": WP_CLIENT_ID,
        "redirect_uri": WP_REDIRECT_URI,
        "client_secret": WP_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }).json()
    access_token = res["access_token"]
    refresh_token = res.get("refresh_token")

    WordPressToken.objects.update_or_create(
        user=request.user,
        defaults={"access_token": access_token, "refresh_token": refresh_token}
    )
    return redirect("/api/logbooks/")


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

        logbook = get_object_or_404(Logbook, id=logbook_id, user=request.user)
        token_obj = get_object_or_404(WordPressToken, user=request.user)

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

        # Response에 UTF-8 명시
        return Response(
            {"wordpress_url": post_url},
            status=status.HTTP_201_CREATED,
            content_type="application/json; charset=utf-8"
        )
