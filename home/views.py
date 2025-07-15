from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auths.models import User
from home.models import Job
from home.serializers import JobSerializer


# Create your views here.
class TopLevelMembersList(APIView):
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


class JobViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'destroy':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user == instance.user:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)


