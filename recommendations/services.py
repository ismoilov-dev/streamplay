"""
Soddalashtirilgan tavsiyalar tizimi.
- Content-based filtering (janr bo'yicha)
- Collaborative filtering (o'xshash foydalanuvchilar)
"""
from collections import Counter
from django.db.models import Count, Q

from content.models import Movie, Series
from analytics.models import WatchHistory, Favorite


def get_user_preferred_genres(user, limit=5):
    """Foydalanuvchining sevimli janrlarini aniqlash."""
    genre_counter = Counter()

    # Tarixdan
    history = WatchHistory.objects.filter(user=user).select_related(
        'movie', 'episode__season__series',
    )
    for h in history[:200]:
        source = h.movie if h.movie_id else (h.episode.season.series if h.episode_id else None)
        if source:
            for g in source.genres.all():
                genre_counter[g.id] += 1

    # Sevimlilardan
    favorites = Favorite.objects.filter(user=user).select_related('movie', 'series')
    for f in favorites:
        source = f.movie or f.series
        if source:
            for g in source.genres.all():
                genre_counter[g.id] += 2  # Sevimli kuchliroq signal

    return [gid for gid, _ in genre_counter.most_common(limit)]


def recommend_movies_for_user(user, limit=20):
    """Foydalanuvchiga mos filmlar tavsiyasi."""
    preferred_genre_ids = get_user_preferred_genres(user)

    # Foydalanuvchi ko'rgan filmlar ID lari
    watched_movie_ids = WatchHistory.objects.filter(
        user=user, movie__isnull=False,
    ).values_list('movie_id', flat=True).distinct()

    qs = Movie.objects.filter(is_published=True).exclude(id__in=watched_movie_ids)

    if preferred_genre_ids:
        qs = qs.filter(genres__id__in=preferred_genre_ids).distinct()

    # Agar tavsiyalar oz bo'lsa — mashhur filmlar bilan to'ldiramiz
    qs = qs.order_by('-imdb_rating', '-views_count')[:limit]

    if qs.count() < limit:
        extra = Movie.objects.filter(is_published=True).exclude(
            id__in=list(qs.values_list('id', flat=True)) + list(watched_movie_ids),
        ).order_by('-views_count')[:limit - qs.count()]
        return list(qs) + list(extra)

    return list(qs)


def recommend_series_for_user(user, limit=20):
    preferred_genre_ids = get_user_preferred_genres(user)

    watched_series_ids = WatchHistory.objects.filter(
        user=user, episode__isnull=False,
    ).values_list('episode__season__series_id', flat=True).distinct()

    qs = Series.objects.filter(is_published=True).exclude(id__in=watched_series_ids)

    if preferred_genre_ids:
        qs = qs.filter(genres__id__in=preferred_genre_ids).distinct()

    qs = qs.order_by('-imdb_rating', '-views_count')[:limit]

    if qs.count() < limit:
        extra = Series.objects.filter(is_published=True).exclude(
            id__in=list(qs.values_list('id', flat=True)) + list(watched_series_ids),
        ).order_by('-views_count')[:limit - qs.count()]
        return list(qs) + list(extra)

    return list(qs)


def similar_movies(movie, limit=10):
    """Ushbu filmga o'xshash filmlar (janr bo'yicha)."""
    genre_ids = list(movie.genres.values_list('id', flat=True))
    if not genre_ids:
        return Movie.objects.filter(is_published=True).exclude(pk=movie.pk).order_by('-views_count')[:limit]

    return (
        Movie.objects.filter(is_published=True, genres__id__in=genre_ids)
        .exclude(pk=movie.pk)
        .annotate(matching_genres=Count('genres', filter=Q(genres__id__in=genre_ids)))
        .order_by('-matching_genres', '-imdb_rating')
        .distinct()[:limit]
    )


def similar_series(series, limit=10):
    genre_ids = list(series.genres.values_list('id', flat=True))
    if not genre_ids:
        return Series.objects.filter(is_published=True).exclude(pk=series.pk).order_by('-views_count')[:limit]

    return (
        Series.objects.filter(is_published=True, genres__id__in=genre_ids)
        .exclude(pk=series.pk)
        .annotate(matching_genres=Count('genres', filter=Q(genres__id__in=genre_ids)))
        .order_by('-matching_genres', '-imdb_rating')
        .distinct()[:limit]
    )
