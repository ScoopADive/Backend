from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from recommend.models import Spot
from recommend.ai_system import CustomPrompt, AsyncCustomPrompt
from recommend.serializers import SpotSerializer

class SpotsRecommendView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        spots = Spot.objects.filter(user_id=request.user.id)
        serializer = SpotSerializer(spots, many=True)
        return Response(serializer.data)

    def post(self, request):
        # SPOT 전부 초기화 (POST 자체만으로 새로 프롬프트를 날려 스팟 정보를 초기화 하겠다는 뜻임)
        # POST 는 사용자가 본인의 Preferences를 업데이트할 시에만 하는 것으로 하든, 아니면 주기적으로 (ex 세번 접속시) 업데이트 하는 것으로 함
        Spot.objects.filter(user_id=request.user.id).delete()
        spots = CustomPrompt(request.user).openai_request()

        for s in spots:
            Spot.objects.create(
                user=request.user,
                region=s.region,
                country=s.country,
                intro=s.intro
            )

        return Response({"message": "Spots updated"}, status=201)


from asgiref.sync import async_to_sync

class AsyncSpotsRecommendView(APIView):

    permission_classes = [IsAuthenticated]

    async def post(self, request):
        # SPOT 전부 초기화 (POST 자체만으로 새로 프롬프트를 날려 스팟 정보를 초기화 하겠다는 뜻임)
        # POST 는 사용자가 본인의 Preferences를 업데이트할 시에만 하는 것으로 하든, 아니면 주기적으로 (ex 세번 접속시) 업데이트 하는 것으로 함
        Spot.objects.filter(user_id=request.user.id).delete()
        spots = async_to_sync(AsyncCustomPrompt(request.user).async_openai_request)()

        for s in spots:
            Spot.objects.create(
                user=request.user,
                region=s.region,
                country=s.country,
                intro=s.intro
            )

        return Response({"message": "Spots updated"}, status=201)


class SpotView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, spot_id):
        spot = get_object_or_404(Spot, id=spot_id)
        serializer = SpotSerializer(spot)
        return Response(serializer.data)
