from django.urls import path

from recommend.views import SpotsRecommendView, SpotView, AsyncSpotsRecommendView

app_name = 'recommend'
urlpatterns = [
    path('spots/', SpotsRecommendView.as_view(), name='spots_recommendation'),
    path('async_spots/', AsyncSpotsRecommendView.as_view(), name='async_spots_recommendation'),
    path('spots/<int:spot_id>/', SpotView.as_view(), name='spot'),
]