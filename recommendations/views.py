from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from content.models import Movie, Series
from content.serializers import MovieListSerializer, SeriesListSerializer
from .services import (
    recommend_movies_for_user, recommend_series_for_user,
    similar_movies, similar_series,
)


@extend_schema(
    tags=['recommendations'],
    responses={200: MovieListSerializer(many=True)},
    description='Foydalanuvchiga shaxsiy film tavsiyalari.',
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_movie_recommendations(request):
    movies = recommend_movies_for_user(request.user)
    data = MovieListSerializer(movies, many=True, context={'request': request}).data
    return Response({'count': len(data), 'results': data})


@extend_schema(
    tags=['recommendations'],
    responses={200: SeriesListSerializer(many=True)},
    description='Foydalanuvchiga shaxsiy serial tavsiyalari.',
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_series_recommendations(request):
    series = recommend_series_for_user(request.user)
    data = SeriesListSerializer(series, many=True, context={'request': request}).data
    return Response({'count': len(data), 'results': data})


@extend_schema(
    tags=['recommendations'],
    parameters=[OpenApiParameter(name='slug', location='path', type=str)],
    responses={200: MovieListSerializer(many=True)},
    description='Berilgan filmga o\'xshash filmlar ro\'yxati.',
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def similar_to_movie(request, slug):
    movie = get_object_or_404(Movie, slug=slug, is_published=True)
    movies = similar_movies(movie)
    data = MovieListSerializer(movies, many=True, context={'request': request}).data
    return Response({'count': len(data), 'results': data})


@extend_schema(
    tags=['recommendations'],
    parameters=[OpenApiParameter(name='slug', location='path', type=str)],
    responses={200: SeriesListSerializer(many=True)},
    description='Berilgan serialga o\'xshash seriallar ro\'yxati.',
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def similar_to_series(request, slug):
    series = get_object_or_404(Series, slug=slug, is_published=True)
    items = similar_series(series)
    data = SeriesListSerializer(items, many=True, context={'request': request}).data
    return Response({'count': len(data), 'results': data})
