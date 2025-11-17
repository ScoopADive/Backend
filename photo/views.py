import uuid
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
import boto3

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif"]

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-uploaded_at')
    serializer_class = PhotoSerializer

    # -----------------------------
    # S3 presigned URL 생성
    # -----------------------------
    @action(detail=False, methods=['get'], url_path='generate_presigned_url')
    def generate_presigned_url(self, request):
        file_name = request.GET.get('filename')
        file_type = request.GET.get('filetype')

        if not file_name or not file_type:
            return Response({"error": "filename and filetype are required"}, status=400)

        if file_type not in ALLOWED_TYPES:
            return Response({"error": "Unsupported file type"}, status=400)

        key = f"uploads/{uuid.uuid4().hex}_{file_name}"

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': key,
                'ContentType': file_type,
            },
            ExpiresIn=3600  # 1시간
        )

        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{key}"

        return Response({'uploadUrl': presigned_url, 'fileUrl': file_url})

    # -----------------------------
    # Fishial 분류
    # -----------------------------
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

            filename = photo.image_url.split("/")[-1]
            content_type, _ = mimetypes.guess_type(filename)
            if content_type not in ALLOWED_TYPES:
                return Response({"error": f"Unsupported content type: {content_type}"}, status=400)

            # S3에서 파일 가져오기
            r = requests.get(photo.image_url)
            r.raise_for_status()
            file_bytes = r.content
            byte_size = len(file_bytes)
            checksum = base64.b64encode(hashlib.md5(file_bytes).digest()).decode()

            # Fishial signed-id 발급
            upload_resp = client.request_signed_upload(token, filename, content_type, byte_size, checksum)
            signed_id = upload_resp["signed-id"]

            print("#### FISHIAL #####")
            print("Token:", token)
            print("Signed ID:", signed_id)
            print("Checksum:", checksum)
            print("Byte size:", byte_size)
            print("#################")


            # Fishial 인식 호출
            result = client.recognize(token, signed_id)

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
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        params = {"q": signed_id}
        r = requests.get(self.RECOG_URL, headers=headers, params=params)
        r.raise_for_status()
        return r.json()
