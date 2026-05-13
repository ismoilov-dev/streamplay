from rest_framework import serializers
from .models import WatchProgress, WatchHistory, BufferingEvent, Favorite


class WatchProgressSerializer(serializers.ModelSerializer):
    percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = WatchProgress
        fields = [
            'id', 'user', 'movie', 'episode',
            'position_seconds', 'duration_seconds', 'completed',
            'percentage', 'updated_at',
        ]
        read_only_fields = ['user', 'updated_at', 'percentage']

    def validate(self, attrs):
        movie = attrs.get('movie')
        episode = attrs.get('episode')
        if not movie and not episode:
            raise serializers.ValidationError("Film yoki epizod tanlanishi kerak.")
        if movie and episode:
            raise serializers.ValidationError("Faqat bittasi: film yoki epizod.")
        return attrs


class UpdateProgressSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField(required=False)
    episode_id = serializers.IntegerField(required=False)
    position_seconds = serializers.IntegerField(min_value=0)
    duration_seconds = serializers.IntegerField(min_value=0, required=False)

    def validate(self, attrs):
        if not attrs.get('movie_id') and not attrs.get('episode_id'):
            raise serializers.ValidationError("movie_id yoki episode_id berilishi kerak.")
        return attrs


class WatchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchHistory
        fields = [
            'id', 'user', 'movie', 'episode', 'watched_seconds',
            'device', 'ip_address', 'started_at',
        ]
        read_only_fields = ['user', 'ip_address', 'started_at']


class BufferingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BufferingEvent
        fields = [
            'id', 'user', 'video_file', 'position_seconds',
            'duration_ms', 'network_type', 'cdn_node', 'created_at',
        ]
        read_only_fields = ['user', 'created_at']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'movie', 'series', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate(self, attrs):
        movie = attrs.get('movie')
        series = attrs.get('series')
        if not movie and not series:
            raise serializers.ValidationError("Film yoki serial tanlanishi kerak.")
        if movie and series:
            raise serializers.ValidationError("Faqat bittasi: film yoki serial.")
        return attrs
