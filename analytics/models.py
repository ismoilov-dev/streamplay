from django.conf import settings
from django.db import models


class WatchProgress(models.Model):
    """Foydalanuvchi video qayerda to'xtaganini saqlash."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watch_progress',
    )
    movie = models.ForeignKey(
        'content.Movie', on_delete=models.CASCADE, blank=True, null=True, related_name='watch_progress',
    )
    episode = models.ForeignKey(
        'content.Episode', on_delete=models.CASCADE, blank=True, null=True, related_name='watch_progress',
    )
    position_seconds = models.PositiveIntegerField(default=0, help_text="Qayerda to'xtagan (soniya)")
    duration_seconds = models.PositiveIntegerField(default=0, help_text="Umumiy davomiyligi")
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ko'rish progressi"
        verbose_name_plural = "Ko'rish progresslari"
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie'],
                condition=models.Q(movie__isnull=False),
                name='unique_user_movie_progress',
            ),
            models.UniqueConstraint(
                fields=['user', 'episode'],
                condition=models.Q(episode__isnull=False),
                name='unique_user_episode_progress',
            ),
        ]

    @property
    def percentage(self):
        if self.duration_seconds == 0:
            return 0
        return round((self.position_seconds / self.duration_seconds) * 100, 2)

    def __str__(self):
        target = self.movie or self.episode or 'N/A'
        return f"{self.user.username} — {target} ({self.percentage}%)"


class WatchHistory(models.Model):
    """Ko'rishlar tarixi — har bir sessiya."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watch_history',
    )
    movie = models.ForeignKey(
        'content.Movie', on_delete=models.CASCADE, blank=True, null=True,
    )
    episode = models.ForeignKey(
        'content.Episode', on_delete=models.CASCADE, blank=True, null=True,
    )
    watched_seconds = models.PositiveIntegerField(default=0)
    device = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ko'rish tarixi"
        verbose_name_plural = "Ko'rish tarixlari"
        ordering = ['-started_at']

    def __str__(self):
        target = self.movie or self.episode or 'N/A'
        return f"{self.user.username} — {target}"


class BufferingEvent(models.Model):
    """Buffering (video qotib qolish) eventlari — QoE analitikasi."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    video_file = models.ForeignKey(
        'content.VideoFile', on_delete=models.CASCADE, related_name='buffering_events',
    )
    position_seconds = models.PositiveIntegerField(default=0)
    duration_ms = models.PositiveIntegerField(default=0, help_text="Buffering qancha davom etdi")
    network_type = models.CharField(max_length=30, blank=True, help_text="wifi / 4g / 5g / ethernet")
    cdn_node = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Buffering event'
        verbose_name_plural = 'Buffering eventlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"Buffering — {self.video_file} ({self.duration_ms}ms)"


class Favorite(models.Model):
    """Foydalanuvchining sevimli filmlari/seriallari."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites',
    )
    movie = models.ForeignKey(
        'content.Movie', on_delete=models.CASCADE, blank=True, null=True,
    )
    series = models.ForeignKey(
        'content.Series', on_delete=models.CASCADE, blank=True, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sevimli'
        verbose_name_plural = 'Sevimlilar'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie'],
                condition=models.Q(movie__isnull=False),
                name='unique_user_favorite_movie',
            ),
            models.UniqueConstraint(
                fields=['user', 'series'],
                condition=models.Q(series__isnull=False),
                name='unique_user_favorite_series',
            ),
        ]

    def __str__(self):
        target = self.movie or self.series or 'N/A'
        return f"{self.user.username} — {target}"
