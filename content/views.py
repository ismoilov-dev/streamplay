from django.db.models import F, Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import (
    Genre, Actor, Movie, Series, Season, Episode,
    VideoFile, Subtitle, AudioTrack,
)
from .serializers import (
    GenreSerializer, ActorSerializer,
    MovieListSerializer, MovieDetailSerializer,
    SeriesListSerializer, SeriesDetailSerializer,
    SeasonSerializer, EpisodeSerializer,
    VideoFileSerializer, SubtitleSerializer, AudioTrackSerializer,
)
from .filters import MovieFilter, SeriesFilter, EpisodeFilter


@extend_schema_view(
    list=extend_schema(tags=['genres']),
    retrieve=extend_schema(tags=['genres']),
    create=extend_schema(tags=['genres']),
    update=extend_schema(tags=['genres']),
    partial_update=extend_schema(tags=['genres']),
    destroy=extend_schema(tags=['genres']),
)
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    search_fields = ['name']
    ordering_fields = ['name']


@extend_schema_view(
    list=extend_schema(tags=['actors']),
    retrieve=extend_schema(tags=['actors']),
    create=extend_schema(tags=['actors']),
    update=extend_schema(tags=['actors']),
    partial_update=extend_schema(tags=['actors']),
    destroy=extend_schema(tags=['actors']),
)
class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    lookup_field = 'slug'
    search_fields = ['full_name', 'biography']
    ordering_fields = ['full_name', 'birth_date']


@extend_schema_view(
    list=extend_schema(tags=['movies']),
    retrieve=extend_schema(tags=['movies']),
    create=extend_schema(tags=['movies']),
    update=extend_schema(tags=['movies']),
    partial_update=extend_schema(tags=['movies']),
    destroy=extend_schema(tags=['movies']),
    trending=extend_schema(tags=['movies']),
    new_releases=extend_schema(tags=['movies']),
    increment_views=extend_schema(tags=['movies']),
)
class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.filter(is_published=True).prefetch_related(
        'genres', 'actors', 'video_files',
    )
    lookup_field = 'slug'
    filterset_class = MovieFilter
    search_fields = ['title', 'original_title', 'description', 'director']
    ordering_fields = ['release_year', 'imdb_rating', 'views_count', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        return MovieDetailSerializer

    def get_queryset(self):
        qs = Movie.objects.prefetch_related('genres', 'actors', 'video_files')
        # Non-staff foydalanuvchilar faqat published ko'radi
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_published=True)
        return qs

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Eng ko'p ko'rilgan filmlar."""
        qs = self.get_queryset().order_by('-views_count')[:20]
        serializer = MovieListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='new-releases')
    def new_releases(self, request):
        """Yangi qo'shilgan filmlar."""
        qs = self.get_queryset().order_by('-created_at')[:20]
        serializer = MovieListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='increment-views')
    def increment_views(self, request, slug=None):
        """Ko'rishlar sonini 1 ga oshirish (atomik)."""
        movie = self.get_object()
        Movie.objects.filter(pk=movie.pk).update(views_count=F('views_count') + 1)
        movie.refresh_from_db()
        return Response({'views_count': movie.views_count})


@extend_schema_view(
    list=extend_schema(tags=['series']),
    retrieve=extend_schema(tags=['series']),
    create=extend_schema(tags=['series']),
    update=extend_schema(tags=['series']),
    partial_update=extend_schema(tags=['series']),
    destroy=extend_schema(tags=['series']),
    trending=extend_schema(tags=['series']),
    new_releases=extend_schema(tags=['series']),
)
class SeriesViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    filterset_class = SeriesFilter
    search_fields = ['title', 'original_title', 'description']
    ordering_fields = ['release_year', 'imdb_rating', 'views_count', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return SeriesListSerializer
        return SeriesDetailSerializer

    def get_queryset(self):
        qs = Series.objects.prefetch_related('genres', 'actors', 'seasons__episodes')
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_published=True)
        return qs

    @action(detail=False, methods=['get'])
    def trending(self, request):
        qs = self.get_queryset().order_by('-views_count')[:20]
        serializer = SeriesListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='new-releases')
    def new_releases(self, request):
        qs = self.get_queryset().order_by('-created_at')[:20]
        serializer = SeriesListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=['seasons']),
    retrieve=extend_schema(tags=['seasons']),
    create=extend_schema(tags=['seasons']),
    update=extend_schema(tags=['seasons']),
    partial_update=extend_schema(tags=['seasons']),
    destroy=extend_schema(tags=['seasons']),
)
class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.prefetch_related('episodes').select_related('series')
    serializer_class = SeasonSerializer
    filterset_fields = ['series']


@extend_schema_view(
    list=extend_schema(tags=['episodes']),
    retrieve=extend_schema(tags=['episodes']),
    create=extend_schema(tags=['episodes']),
    update=extend_schema(tags=['episodes']),
    partial_update=extend_schema(tags=['episodes']),
    destroy=extend_schema(tags=['episodes']),
    increment_views=extend_schema(tags=['episodes']),
)
class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.select_related('season__series').prefetch_related('video_files')
    serializer_class = EpisodeSerializer
    filterset_class = EpisodeFilter
    search_fields = ['title', 'description']
    ordering_fields = ['number', 'air_date', 'views_count']

    @action(detail=True, methods=['post'], url_path='increment-views')
    def increment_views(self, request, pk=None):
        episode = self.get_object()
        Episode.objects.filter(pk=episode.pk).update(views_count=F('views_count') + 1)
        episode.refresh_from_db()
        return Response({'views_count': episode.views_count})


@extend_schema_view(
    list=extend_schema(tags=['video-files']),
    retrieve=extend_schema(tags=['video-files']),
    create=extend_schema(tags=['video-files']),
    update=extend_schema(tags=['video-files']),
    partial_update=extend_schema(tags=['video-files']),
    destroy=extend_schema(tags=['video-files']),
)
class VideoFileViewSet(viewsets.ModelViewSet):
    queryset = VideoFile.objects.prefetch_related('subtitles', 'audio_tracks')
    serializer_class = VideoFileSerializer
    filterset_fields = ['movie', 'episode', 'quality', 'status']


@extend_schema_view(
    list=extend_schema(tags=['subtitles']),
    retrieve=extend_schema(tags=['subtitles']),
    create=extend_schema(tags=['subtitles']),
    update=extend_schema(tags=['subtitles']),
    partial_update=extend_schema(tags=['subtitles']),
    destroy=extend_schema(tags=['subtitles']),
)
class SubtitleViewSet(viewsets.ModelViewSet):
    queryset = Subtitle.objects.select_related('video_file')
    serializer_class = SubtitleSerializer
    filterset_fields = ['video_file', 'language']


@extend_schema_view(
    list=extend_schema(tags=['audio-tracks']),
    retrieve=extend_schema(tags=['audio-tracks']),
    create=extend_schema(tags=['audio-tracks']),
    update=extend_schema(tags=['audio-tracks']),
    partial_update=extend_schema(tags=['audio-tracks']),
    destroy=extend_schema(tags=['audio-tracks']),
)
class AudioTrackViewSet(viewsets.ModelViewSet):
    queryset = AudioTrack.objects.select_related('video_file')
    serializer_class = AudioTrackSerializer
    filterset_fields = ['video_file', 'language']


# ========== Search ==========

@extend_schema(
    tags=['search'],
    parameters=[
        OpenApiParameter(name='q', description='Qidiruv so\'zi', required=True, type=str),
        OpenApiParameter(name='type', description='all | movies | series', required=False, type=str),
    ],
    responses={200: dict},
    description='Filmlar va seriallar bo\'yicha umumiy qidiruv.',
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def global_search(request):
    """Umumiy qidiruv (Movie + Series)."""
    query = (request.query_params.get('q') or '').strip()
    kind = request.query_params.get('type', 'all')

    if not query:
        return Response({'results': {'movies': [], 'series': []}, 'count': 0})

    result = {'movies': [], 'series': []}

    if kind in ('all', 'movies'):
        movies = Movie.objects.filter(is_published=True).filter(
            Q(title__icontains=query) |
            Q(original_title__icontains=query) |
            Q(description__icontains=query) |
            Q(director__icontains=query) |
            Q(actors__full_name__icontains=query) |
            Q(genres__name__icontains=query)
        ).distinct()[:20]
        result['movies'] = MovieListSerializer(movies, many=True, context={'request': request}).data

    if kind in ('all', 'series'):
        series = Series.objects.filter(is_published=True).filter(
            Q(title__icontains=query) |
            Q(original_title__icontains=query) |
            Q(description__icontains=query) |
            Q(actors__full_name__icontains=query) |
            Q(genres__name__icontains=query)
        ).distinct()[:20]
        result['series'] = SeriesListSerializer(series, many=True, context={'request': request}).data

    return Response({
        'query': query,
        'count': len(result['movies']) + len(result['series']),
        'results': result,
    })
