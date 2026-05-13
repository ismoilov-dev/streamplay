from datetime import timedelta
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SubscriptionPlan, Subscription, Payment
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer,
    SubscribeSerializer, PaymentSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['subscriptions']),
    retrieve=extend_schema(tags=['subscriptions']),
    create=extend_schema(tags=['subscriptions']),
    update=extend_schema(tags=['subscriptions']),
    partial_update=extend_schema(tags=['subscriptions']),
    destroy=extend_schema(tags=['subscriptions']),
)
class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


@extend_schema_view(
    list=extend_schema(tags=['subscriptions']),
    retrieve=extend_schema(tags=['subscriptions']),
    create=extend_schema(tags=['subscriptions']),
    my_subscription=extend_schema(tags=['subscriptions']),
    subscribe=extend_schema(tags=['subscriptions'], request=SubscribeSerializer),
    cancel=extend_schema(tags=['subscriptions']),
)
class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Subscription.objects.none()
        user = self.request.user
        if user.is_staff:
            return Subscription.objects.select_related('plan', 'user')
        return Subscription.objects.filter(user=user).select_related('plan', 'user')

    @action(detail=False, methods=['get'], url_path='my-subscription')
    def my_subscription(self, request):
        """Hozirgi foydalanuvchining faol obunasi."""
        sub = Subscription.objects.filter(
            user=request.user, status='active', expires_at__gt=timezone.now(),
        ).select_related('plan').order_by('-expires_at').first()
        if not sub:
            return Response({'active': False, 'message': "Faol obuna mavjud emas."})
        return Response({'active': True, 'subscription': SubscriptionSerializer(sub).data})

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """Rejaga obuna bo'lish (soddalashtirilgan, to'lov tizimisiz)."""
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = SubscriptionPlan.objects.get(pk=serializer.validated_data['plan_id'])
        now = timezone.now()

        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status='active',
            started_at=now,
            expires_at=now + timedelta(days=plan.duration_days),
            auto_renew=serializer.validated_data['auto_renew'],
        )

        # Avtomatik to'lov yozuvi yaratamiz (sandbox)
        Payment.objects.create(
            user=request.user,
            subscription=subscription,
            amount=plan.price,
            currency=plan.currency,
            provider='manual',
            status='completed',
            completed_at=now,
        )

        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Obunani bekor qilish."""
        subscription = self.get_object()
        subscription.status = 'cancelled'
        subscription.auto_renew = False
        subscription.save()
        return Response({'message': 'Obuna bekor qilindi.', 'subscription': SubscriptionSerializer(subscription).data})


@extend_schema_view(
    list=extend_schema(tags=['subscriptions']),
    retrieve=extend_schema(tags=['subscriptions']),
)
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        user = self.request.user
        if user.is_staff:
            return Payment.objects.select_related('subscription', 'user')
        return Payment.objects.filter(user=user).select_related('subscription', 'user')
