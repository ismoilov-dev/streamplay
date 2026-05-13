from django.urls import path

from .views import (
    my_movie_recommendations, my_series_recommendations,
    similar_to_movie, similar_to_series,
)

urlpatterns = [
    path('movies/for-me/', my_movie_recommendations, name='rec-my-movies'),
    path('series/for-me/', my_series_recommendations, name='rec-my-series'),
    path('movies/similar/<slug:slug>/', similar_to_movie, name='rec-similar-movies'),
    path('series/similar/<slug:slug>/', similar_to_series, name='rec-similar-series'),
]
