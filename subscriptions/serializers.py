from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, Payment


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'currency', 'period',
            'duration_days', 'max_quality', 'max_concurrent_streams',
            'allows_downloads', 'is_active', 'created_at',
        ]
        read_only_fields = ['created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'plan', 'plan_details', 'status',
            'started_at', 'expires_at', 'auto_renew', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'is_active']


class SubscribeSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    auto_renew = serializers.BooleanField(default=False)

    def validate_plan_id(self, value):
        if not SubscriptionPlan.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Bunday faol reja topilmadi.")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'subscription', 'amount', 'currency',
            'provider', 'status', 'external_id',
            'created_at', 'completed_at',
        ]
        read_only_fields = ['user', 'created_at', 'completed_at']
