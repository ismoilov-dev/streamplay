from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from content.models import Movie, Episode
from .models import WatchProgress, WatchHistory, BufferingEvent, Favorite
from .serializers import (
    WatchProgressSerializer, UpdateProgressSerializer,
    WatchHistorySerializer, BufferingEventSerializer, FavoriteSerializer,
)


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@extend_schema_view(
    list=extend_schema(tags=['watch-progress']),
    retrieve=extend_schema(tags=['watch-progress']),
    create=extend_schema(tags=['watch-progress']),
    update=extend_schema(tags=['watch-progress']),
    partial_update=extend_schema(tags=['watch-progress']),
    destroy=extend_schema(tags=['watch-progress']),
    update_progress=extend_schema(tags=['watch-progress'], request=UpdateProgressSerializer),
    continue_watching=extend_schema(tags=['watch-progress']),
)
class WatchProgressViewSet(viewsets.ModelViewSet):
    serializer_class = WatchProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WatchProgress.objects.none()
        return WatchProgress.objects.filter(user=self.request.user).select_related(
            'movie', 'episode',
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='update')
    def update_progress(self, request):
        """
        Video ko'rish progressini yangilash (upsert).
        Frontend har 10 soniyada bu endpointga so'rov yuboradi.
        """
        serializer = UpdateProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        lookup = {'user': request.user}
        if data.get('movie_id'):
            if not Movie.objects.filter(pk=data['movie_id']).exists():
                return Response(
                    {'movie_id': 'Bunday film topilmadi.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            lookup['movie_id'] = data['movie_id']
        else:
            if not Episode.objects.filter(pk=data['episode_id']).exists():
                return Response(
                    {'episode_id': 'Bunday epizod topilmadi.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            lookup['episode_id'] = data['episode_id']

        defaults = {
            'position_seconds': data['position_seconds'],
        }
        if data.get('duration_seconds') is not None:
            defaults['duration_seconds'] = data['duration_seconds']
            # 95%+ bo'lsa, tugagan deb belgilaymiz
            if data['duration_seconds'] > 0 and data['position_seconds'] / data['duration_seconds'] >= 0.95:
                defaults['completed'] = True

        progress, _ = WatchProgress.objects.update_or_create(defaults=defaults, **lookup)
        return Response(WatchProgressSerializer(progress).data)

    @action(detail=False, methods=['get'], url_path='continue-watching')
    def continue_watching(self, request):
        """Davom ettirishga mos — tugatmagan va oxirgi marta ko'rilgan videolar."""
        qs = self.get_queryset().filter(completed=False, position_seconds__gt=0)[:20]
        return Response(WatchProgressSerializer(qs, many=True).data)


@extend_schema_view(
    list=extend_schema(tags=['history']),
    retrieve=extend_schema(tags=['history']),
    create=extend_schema(tags=['history']),
    destroy=extend_schema(tags=['history']),
    clear=extend_schema(tags=['history']),
)
class WatchHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = WatchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WatchHistory.objects.none()
        return WatchHistory.objects.filter(user=self.request.user).select_related(
            'movie', 'episode',
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, ip_address=_get_client_ip(self.request))

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Butun tarixni tozalash."""
        deleted, _ = self.get_queryset().delete()
        return Response({'deleted': deleted, 'message': 'Tarix tozalandi.'})


@extend_schema_view(
    list=extend_schema(tags=['analytics']),
    retrieve=extend_schema(tags=['analytics']),
    create=extend_schema(tags=['analytics']),
)
class BufferingEventViewSet(viewsets.ModelViewSet):
    serializer_class = BufferingEventSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticatedOrReadOnly()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        return BufferingEvent.objects.select_related('user', 'video_file')

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


@extend_schema_view(
    list=extend_schema(tags=['users']),
    retrieve=extend_schema(tags=['users']),
    create=extend_schema(tags=['users']),
    destroy=extend_schema(tags=['users']),
)
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user).select_related(
            'movie', 'series',
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
