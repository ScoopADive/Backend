import hashlib
import base64
import mimetypes
import requests

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from photo.models import Photo
from photo.serializers import PhotoSerializer


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

    def request_signed_upload(self, token, filename, content_type, byte_size, checksum):
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

    def recognize(self, token, signed_id):
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        params = {"q": signed_id}
        r = requests.get(self.RECOG_URL, headers=headers, params=params)
        r.raise_for_status()
        return r.json()


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
            # 1️⃣ Access Token 발급
            token = client.get_token()

            # 2️⃣ 이미지 메타데이터 계산
            filename = photo.image_url.split("/")[-1]
            content_type, _ = mimetypes.guess_type(filename)
            if content_type not in ["image/jpeg", "image/png", "image/gif"]:
                return Response({"error": f"Unsupported content type: {content_type}"}, status=400)

            r = requests.get(photo.image_url)
            r.raise_for_status()
            file_bytes = r.content
            byte_size = len(file_bytes)
            checksum = base64.b64encode(hashlib.md5(file_bytes).digest()).decode()

            # 3️⃣ Signed Upload 요청
            upload_resp = client.request_signed_upload(token, filename, content_type, byte_size, checksum)
            signed_id = upload_resp["signed-id"]
            direct_upload = upload_resp["direct-upload"]
            upload_url = direct_upload["url"]
            headers = direct_upload.get("headers", {})

            # 4️⃣ Direct Upload to S3
            put_headers = {
                "Content-Disposition": headers.get("Content-Disposition"),
                "Content-MD5": headers.get("Content-MD5"),
                "Content-Type": "",  # 반드시 비워두기
            }
            put_resp = requests.put(upload_url, headers=put_headers, data=file_bytes)
            put_resp.raise_for_status()

            # 5️⃣ Fishial Recognition
            result = client.recognize(token, signed_id)

            photo.classified_as = result["fishial_result"]["results"][0]["species"][0]["name"]

            return Response({
                "photo_id": photo.id,
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
