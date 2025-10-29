from rest_framework.response import Response
from rest_framework.views import APIView
from ai.models import Spot
from ai.ai_system import CustomPrompt
from ai.serializers import SpotSerializer

class SpotsRecommendationView(APIView):

    def get(self, request):
        spots = Spot.objects.filter(user_id=request.user.id)
        serializer = SpotSerializer(spots, many=True)
        return Response(serializer.data)

    def post(self, request):
        # SPOT 전부 초기화 (POST 자체만으로 새로 프롬프트를 날려 스팟 정보를 초기화 하겠다는 뜻임)
        # POST 는 사용자가 본인의 Preferences를 업데이트할 시에만 하는 것으로 하든, 아니면 주기적으로 (ex 세번 접속시) 업데이트 하는 것으로 함
        spots = Spot.objects.all()
        spots.delete()

        spots = CustomPrompt(request.user).run_prompt()

        for i in range(len(spots)):
            spot = Spot.objects.create()
            spot.user = request.user
            spot.region = spots[i].region
            spot.country = spots[i].country
            spot.intro = spots[i].intro
            spot.save()

class SpotView(APIView):
    def get(self, request, spot_id):
        spot = Spot.objects.get(id=spot_id)
        serializer = SpotSerializer(spot)
        return Response(serializer.data)

