import uuid
import boto3
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from photo.models import Photo
from photo.serializers import PhotoSerializer

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif"]
import requests
from django.conf import settings

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-uploaded_at')
    serializer_class = PhotoSerializer

    @action(detail=False, methods=['get'], url_path='generate_presigned_url')
    def generate_presigned_url(self, request):
        file_name = request.GET.get('filename')
        file_type = request.GET.get('filetype')

        if file_type not in ALLOWED_TYPES:
            return Response({"error": "Invalid file type"}, status=400)

        # 중복 방지 UUID
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


    @action(detail=True, methods=['post'], url_path='classify')
    def classify(self, request, pk=None):
        try:
            photo = Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            return Response({"error": "Photo not found"}, status=404)

        if not photo.image_url:
            return Response({"error": "image_url is empty"}, status=400)

        client = FishClient()

        try:
            result = client.classify(photo.image_url)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({
            "photo_id": photo.id,
            "image_url": photo.image_url,
            "fishial_result": result
        })

class FishClient:
    def __init__(self):
        self.client_id = settings.FISHIAL_CLIENT_ID
        self.client_secret = settings.FISHIAL_CLIENT_SECRET
        self.auth_url = "https://api-users.fishial.ai/v1/auth/token"
        self.identify_url = "https://api.fishial.ai/v1/recognition/image"

    def get_token(self):
        r = requests.post(self.auth_url, json={
            "client_id": self.client_id,
            "client_secret": self.client_secret
        })
        r.raise_for_status()
        return r.json()["access_token"]

    def classify(self, img_url: str):
        token = self.get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {"url": img_url}

        r = requests.post(self.identify_url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
