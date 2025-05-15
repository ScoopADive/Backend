from rest_framework import permissions, viewsets
from rest_framework.parsers import MultiPartParser

from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from logbook.models import Logbook
from .serializers import LogbookSerializer


class LogbookViewSet(viewsets.ModelViewSet):
    queryset = Logbook.objects.all().order_by('-dive_date')
    serializer_class = LogbookSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]  # 이미지 업로드를 위해 필요


    def retrieve(self, request, pk=None):
        logbook = get_object_or_404(Logbook, pk=pk)
        serializer = LogbookSerializer(logbook)
        return Response(serializer.data)
