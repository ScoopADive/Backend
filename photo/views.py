import uuid
import boto3
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from photo.models import Photo
from photo.serializers import PhotoSerializer

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif"]

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-uploaded_at')
    serializer_class = PhotoSerializer

    @api_view(['GET'])
    def generate_presigned_url(request):
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
