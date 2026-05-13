import django_filters
from .models import Movie, Series, Episode


class MovieFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genres__slug', lookup_expr='iexact')
    genre_id = django_filters.NumberFilter(field_name='genres__id')
    year_min = django_filters.NumberFilter(field_name='release_year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='release_year', lookup_expr='lte')
    rating_min = django_filters.NumberFilter(field_name='imdb_rating', lookup_expr='gte')

    class Meta:
        model = Movie
        fields = ['is_premium', 'is_published', 'age_rating', 'country', 'language']


class SeriesFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genres__slug', lookup_expr='iexact')
    genre_id = django_filters.NumberFilter(field_name='genres__id')
    year_min = django_filters.NumberFilter(field_name='release_year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='release_year', lookup_expr='lte')

    class Meta:
        model = Series
        fields = ['is_premium', 'is_published', 'status', 'age_rating']


class EpisodeFilter(django_filters.FilterSet):
    series = django_filters.NumberFilter(field_name='season__series__id')

    class Meta:
        model = Episode
        fields = ['season']
