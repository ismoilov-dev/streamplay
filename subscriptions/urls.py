from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SubscriptionPlanViewSet, SubscriptionViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='plan')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]
