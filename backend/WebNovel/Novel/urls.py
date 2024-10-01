from django.urls import path
from .views import get_novels, get_recommendations

urlpatterns = [
    path('novels/', get_novels, name='get_novels'),
    path('recommendations/', get_recommendations, name='get_recommendations'),
]
