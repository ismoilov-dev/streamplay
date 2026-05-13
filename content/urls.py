from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    GenreViewSet, ActorViewSet,
    MovieViewSet, SeriesViewSet, SeasonViewSet, EpisodeViewSet,
    VideoFileViewSet, SubtitleViewSet, AudioTrackViewSet,
    global_search,
)

router = DefaultRouter()
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'actors', ActorViewSet, basename='actor')
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'series', SeriesViewSet, basename='series')
router.register(r'seasons', SeasonViewSet, basename='season')
router.register(r'episodes', EpisodeViewSet, basename='episode')
router.register(r'video-files', VideoFileViewSet, basename='video-file')
router.register(r'subtitles', SubtitleViewSet, basename='subtitle')
router.register(r'audio-tracks', AudioTrackViewSet, basename='audio-track')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', global_search, name='global-search'),
]
