from rest_framework import serializers
from photo.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    # GET 요청에서만 classified_as를 보여주도록 수정
    classified_as = serializers.SerializerMethodField()

    image_url = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = Photo
        # 필요한 필드만 명시적으로 포함
        fields = ['id', 'title', 'image_url', 'uploaded_at', 'classified_as']

    def get_classified_as(self, obj):
        request = self.context.get('request')
        # GET 요청일 때만 반환, 그 외는 None
        if request and request.method == 'GET':
            return obj.classified_as
        return None
