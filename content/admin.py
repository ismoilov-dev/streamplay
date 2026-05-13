from django.contrib import admin
from .models import (
    Genre, Actor, Movie, Series, Season, Episode,
    VideoFile, Subtitle, AudioTrack,
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date')
    search_fields = ('full_name',)


class VideoFileInline(admin.TabularInline):
    model = VideoFile
    extra = 0


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'age_rating', 'is_premium', 'is_published', 'views_count')
    list_filter = ('is_premium', 'is_published', 'age_rating', 'release_year')
    search_fields = ('title', 'original_title', 'director')
    filter_horizontal = ('genres', 'actors')
    inlines = [VideoFileInline]


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'status', 'is_premium', 'is_published')
    list_filter = ('is_premium', 'is_published', 'status', 'age_rating')
    search_fields = ('title', 'original_title')
    filter_horizontal = ('genres', 'actors')
    inlines = [SeasonInline]


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 0


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('series', 'number', 'title', 'release_year')
    list_filter = ('series',)
    inlines = [EpisodeInline]


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('season', 'number', 'title', 'air_date', 'views_count')
    list_filter = ('season__series',)
    search_fields = ('title',)
    inlines = [VideoFileInline]


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quality', 'status', 'is_encrypted')
    list_filter = ('quality', 'status', 'is_encrypted')


@admin.register(Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    list_display = ('video_file', 'language', 'is_default')
    list_filter = ('language', 'is_default')


@admin.register(AudioTrack)
class AudioTrackAdmin(admin.ModelAdmin):
    list_display = ('video_file', 'language', 'is_default')
    list_filter = ('language', 'is_default')
