from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auths.models import User


# Create your views here.
class TopLevelMember(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        members = User.objects.all()
        name_n_likes = {}

        for member in members:
            count_all_likes = 0
            print(member.own_logbooks.all())
            for logbook in member.own_logbooks.all():
                count_all_likes += logbook.total_likes()
            name_n_likes[member.username] = count_all_likes

        sorted_top_level_members = sorted(name_n_likes.items(), key=lambda x: x[1], reverse=True)[:3]
        return Response(sorted_top_level_members)

