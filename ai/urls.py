from django.urls import path

from ai.views import SpotsRecommendationView, SpotView

app_name = 'ai'
urlpatterns = [
    path('', SpotsRecommendationView.as_view(), name='spots_recommendation'),
    path('<int:spot_id>/', SpotView.as_view(), name='spot'),
]