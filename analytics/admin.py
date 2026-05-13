from django.contrib import admin
from .models import WatchProgress, WatchHistory, BufferingEvent, Favorite


@admin.register(WatchProgress)
class WatchProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'episode', 'position_seconds', 'completed', 'updated_at')
    list_filter = ('completed',)


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'episode', 'watched_seconds', 'device', 'started_at')
    list_filter = ('device',)


@admin.register(BufferingEvent)
class BufferingEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'video_file', 'position_seconds', 'duration_ms', 'network_type', 'created_at')
    list_filter = ('network_type',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'series', 'created_at')
