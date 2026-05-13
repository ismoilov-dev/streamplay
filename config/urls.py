"""
StreamPlay URL Configuration
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def root_view(request):
    """Root endpoint — API haqida qisqacha ma'lumot."""
    return JsonResponse({
        'name': 'StreamPlay API',
        'version': '1.0.0',
        'docs': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
            'schema': '/api/schema/',
        },
        'endpoints': {
            'auth': '/api/auth/',
            'users': '/api/users/',
            'content': '/api/content/',
            'subscriptions': '/api/subscriptions/',
            'analytics': '/api/analytics/',
            'recommendations': '/api/recommendations/',
            'uploads': '/api/uploads/',
            'search': '/api/search/',
        }
    })


urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),

    # OpenAPI schema & docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # App URLs
    path('api/auth/', include('accounts.urls_auth')),
    path('api/users/', include('accounts.urls_users')),
    path('api/', include('content.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    path('api/uploads/', include('uploads.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
