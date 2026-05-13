from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    WatchProgressViewSet, WatchHistoryViewSet,
    BufferingEventViewSet, FavoriteViewSet,
)

router = DefaultRouter()
router.register(r'progress', WatchProgressViewSet, basename='progress')
router.register(r'history', WatchHistoryViewSet, basename='history')
router.register(r'buffering', BufferingEventViewSet, basename='buffering')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]
