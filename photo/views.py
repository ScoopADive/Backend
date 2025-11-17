import hashlib
import base64
import mimetypes

import requests
from django.conf import settings
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from photo.models import Photo
from photo.serializers import PhotoSerializer

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-uploaded_at')
    serializer_class = PhotoSerializer

    @action(detail=True, methods=['post'], url_path='classify')
    def classify(self, request, pk=None):
        try:
            photo = Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            return Response({"error": "Photo not found"}, status=404)

        if not photo.image_url:
            return Response({"error": "image_url is empty"}, status=400)

        client = FishialClient()
        try:
            token = client.get_token()
            print('Fishial token: ', token)
            # S3 URL 기반 Fishial upload
            # 메타데이터 계산
            filename = photo.image_url.split("/")[-1]

            # MIME 타입 추출
            content_type, _ = mimetypes.guess_type(filename)
            if content_type not in ["image/jpeg", "image/png", "image/gif"]:
                return Response({"error": f"Unsupported content type: {content_type}"}, status=400)

            # 실제 S3 접근
            r = requests.get(photo.image_url)
            r.raise_for_status()
            file_bytes = r.content
            byte_size = len(file_bytes)
            checksum = base64.b64encode(hashlib.md5(file_bytes).digest()).decode()
            print('Fishial checksum: ', checksum)

            # 1) signed-id 발급
            upload_resp = client.request_signed_upload(token, filename, content_type, byte_size, checksum)
            print('Fishial upload response: ', upload_resp)
            signed_id = upload_resp["signed-id"]

            # 2) Fishial recognition 호출
            result = client.recognize(token, signed_id)

            return Response({                "photo_id": photo.id,
                "image_url": photo.image_url,
                "fishial_result": result
            })


        except requests.HTTPError as e:
            resp = getattr(e, "response", None)
            try:
                detail = resp.json()
            except Exception:
                detail = str(resp.text) if resp else str(e)
            return Response({"detail": "Fishial API error", "error": detail}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({"detail": "Internal server error", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FishialClient:
    AUTH_URL = "https://api-users.fishial.ai/v1/auth/token"
    UPLOAD_URL = "https://api.fishial.ai/v1/recognition/upload"
    RECOG_URL = "https://api.fishial.ai/v1/recognition/image"

    def __init__(self):
        self.client_id = settings.FISHIAL_CLIENT_ID
        self.client_secret = settings.FISHIAL_CLIENT_SECRET

    def get_token(self) -> str:
        r = requests.post(self.AUTH_URL, json={
            "client_id": self.client_id,
            "client_secret": self.client_secret
        })
        r.raise_for_status()
        return r.json()["access_token"]

    def request_signed_upload(self, token: str, filename: str, content_type: str, byte_size: int, checksum: str):
        """이미지 메타데이터를 보내 signed-id 발급"""
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "blob": {
                "filename": filename,
                "content_type": content_type,
                "byte_size": byte_size,
                "checksum": checksum
            }
        }
        r = requests.post(self.UPLOAD_URL, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()

    def recognize(self, token: str, signed_id: str):
        """signed-id로 Fishial recognition 요청"""
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        params = {"q": signed_id}
        r = requests.get(self.RECOG_URL, headers=headers, params=params)
        r.raise_for_status()
        return r.json()
