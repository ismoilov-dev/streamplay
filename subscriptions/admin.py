from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Payment


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'currency', 'period', 'duration_days', 'is_active')
    list_filter = ('is_active', 'period')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'started_at', 'expires_at', 'auto_renew')
    list_filter = ('status', 'plan', 'auto_renew')
    search_fields = ('user__username', 'user__email')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'provider', 'status', 'created_at')
    list_filter = ('status', 'provider', 'currency')
    search_fields = ('user__username', 'external_id')
