from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


class SubscriptionPlan(models.Model):
    PERIOD_CHOICES = [
        ('monthly', 'Oylik'),
        ('quarterly', 'Chorak (3 oy)'),
        ('yearly', 'Yillik'),
    ]

    name = models.CharField(max_length=100, verbose_name='Nomi')
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='UZS')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    duration_days = models.PositiveIntegerField(default=30)
    max_quality = models.CharField(
        max_length=10,
        default='1080p',
        choices=[('480p', '480p'), ('720p', '720p'), ('1080p', '1080p'), ('2160p', '4K')],
    )
    max_concurrent_streams = models.PositiveIntegerField(default=1)
    allows_downloads = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Obuna rejasi'
        verbose_name_plural = 'Obuna rejalari'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} ({self.price} {self.currency})"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Faol'),
        ('expired', 'Muddati tugagan'),
        ('cancelled', 'Bekor qilingan'),
        ('pending', 'Kutilmoqda'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions',
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Obuna'
        verbose_name_plural = 'Obunalar'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = self.started_at + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == 'active' and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.user.username} — {self.plan.name}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('completed', 'Yakunlangan'),
        ('failed', 'Muvaffaqiyatsiz'),
        ('refunded', 'Qaytarilgan'),
    ]

    PROVIDER_CHOICES = [
        ('click', 'Click'),
        ('payme', 'Payme'),
        ('uzum', 'Uzum'),
        ('visa', 'Visa/Mastercard'),
        ('manual', 'Qo\'lda'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='UZS')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='manual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    external_id = models.CharField(max_length=255, blank=True, help_text="To'lov tizimi tranzaksiya ID")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.amount} {self.currency} ({self.status})"
