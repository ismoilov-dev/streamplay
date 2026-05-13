from rest_framework import serializers

from .models import (
    Genre, Actor, Movie, Series, Season, Episode,
    VideoFile, Subtitle, AudioTrack,
)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['slug']


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'full_name', 'slug', 'biography', 'birth_date', 'photo']
        read_only_fields = ['slug']


class SubtitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtitle
        fields = ['id', 'video_file', 'language', 'language_name', 'file', 'is_default', 'created_at']
        read_only_fields = ['created_at']


class AudioTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioTrack
        fields = ['id', 'video_file', 'language', 'language_name', 'file', 'is_default', 'created_at']
        read_only_fields = ['created_at']


class VideoFileSerializer(serializers.ModelSerializer):
    subtitles = SubtitleSerializer(many=True, read_only=True)
    audio_tracks = AudioTrackSerializer(many=True, read_only=True)

    class Meta:
        model = VideoFile
        fields = [
            'id', 'movie', 'episode', 'quality', 'file',
            'hls_manifest_url', 'dash_manifest_url',
            'size_bytes', 'duration_seconds', 'bitrate_kbps',
            'status', 'is_encrypted',
            'subtitles', 'audio_tracks',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        movie = attrs.get('movie')
        episode = attrs.get('episode')
        if not movie and not episode:
            raise serializers.ValidationError(
                "Video fayl film yoki epizodga tegishli bo'lishi kerak."
            )
        if movie and episode:
            raise serializers.ValidationError(
                "Video fayl faqat film yoki faqat epizodga tegishli bo'la oladi, ikkisiga emas."
            )
        return attrs


class MovieListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'short_description', 'release_year',
            'duration_minutes', 'age_rating', 'imdb_rating',
            'thumbnail', 'poster', 'is_premium', 'views_count',
            'genres',
        ]


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)
    video_files = VideoFileSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, write_only=True, required=False, source='genres',
    )
    actor_ids = serializers.PrimaryKeyRelatedField(
        queryset=Actor.objects.all(), many=True, write_only=True, required=False, source='actors',
    )

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'original_title', 'slug', 'description', 'short_description',
            'release_year', 'country', 'language', 'age_rating', 'imdb_rating',
            'duration_minutes', 'director', 'thumbnail', 'poster', 'trailer_url',
            'is_premium', 'is_published', 'views_count',
            'genres', 'actors', 'video_files',
            'genre_ids', 'actor_ids',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'views_count', 'created_at', 'updated_at']


class EpisodeSerializer(serializers.ModelSerializer):
    video_files = VideoFileSerializer(many=True, read_only=True)

    class Meta:
        model = Episode
        fields = [
            'id', 'season', 'number', 'title', 'description',
            'duration_minutes', 'thumbnail', 'air_date', 'views_count',
            'video_files', 'created_at',
        ]
        read_only_fields = ['views_count', 'created_at']


class SeasonSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = [
            'id', 'series', 'number', 'title', 'description',
            'release_year', 'poster', 'episodes', 'created_at',
        ]
        read_only_fields = ['created_at']


class SeriesListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Series
        fields = [
            'id', 'title', 'slug', 'short_description', 'release_year',
            'status', 'total_seasons', 'total_episodes',
            'age_rating', 'imdb_rating',
            'thumbnail', 'poster', 'is_premium', 'views_count',
            'genres',
        ]


class SeriesDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)
    seasons = SeasonSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, write_only=True, required=False, source='genres',
    )
    actor_ids = serializers.PrimaryKeyRelatedField(
        queryset=Actor.objects.all(), many=True, write_only=True, required=False, source='actors',
    )

    class Meta:
        model = Series
        fields = [
            'id', 'title', 'original_title', 'slug', 'description', 'short_description',
            'release_year', 'country', 'language', 'age_rating', 'imdb_rating',
            'status', 'total_seasons', 'total_episodes',
            'thumbnail', 'poster', 'trailer_url',
            'is_premium', 'is_published', 'views_count',
            'genres', 'actors', 'seasons',
            'genre_ids', 'actor_ids',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'views_count', 'created_at', 'updated_at']
