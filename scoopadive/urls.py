"""
URL configuration for scoopadive project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers, serializers, viewsets, permissions
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers

from auths.views import CustomTokenObtainPairView
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from django.conf.urls.static import static



# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'groups', views.GroupViewSet)


# Swagger UI 적용
schema_view = get_schema_view(
    openapi.Info(
        title="ScoopADive API",
        default_version='v1',
        description="ScoopADive를 위한 유저 API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],  # 여기를 꼭 비워야 기본 인증 안 뜸
)



urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include(router.urls)),
    path("logbooks/", include("logbook.urls")),
    path("auths/", include("auths.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# swagger
urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

