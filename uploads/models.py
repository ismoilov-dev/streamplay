import uuid
from django.conf import settings
from django.db import models


def upload_chunk_path(instance, filename):
    return f'uploads/chunks/{instance.upload.upload_id}/{filename}'


def upload_final_path(instance, filename):
    return f'uploads/final/{instance.upload_id}/{filename}'


class Upload(models.Model):
    """Chunked upload sessiyasi (Tus Protocol soddalashtirilgan)."""

    STATUS_CHOICES = [
        ('in_progress', 'Davom etmoqda'),
        ('completed', 'Tugallangan'),
        ('failed', 'Xatolik'),
        ('cancelled', 'Bekor qilingan'),
    ]

    upload_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploads',
    )
    filename = models.CharField(max_length=500)
    content_type = models.CharField(max_length=200, blank=True)
    total_size = models.BigIntegerField(help_text='Umumiy fayl hajmi (bayt)')
    uploaded_bytes = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    final_file = models.FileField(upload_to=upload_final_path, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Yuklash sessiyasi'
        verbose_name_plural = 'Yuklash sessiyalari'
        ordering = ['-created_at']

    @property
    def progress_percentage(self):
        if self.total_size == 0:
            return 0
        return round((self.uploaded_bytes / self.total_size) * 100, 2)

    def __str__(self):
        return f"{self.filename} ({self.progress_percentage}%)"


class UploadChunk(models.Model):
    """Bitta chunk (bo'lak)."""

    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, related_name='chunks')
    chunk_number = models.PositiveIntegerField()
    file = models.FileField(upload_to=upload_chunk_path)
    size = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chunk'
        verbose_name_plural = 'Chunklar'
        unique_together = ('upload', 'chunk_number')
        ordering = ['chunk_number']

    def __str__(self):
        return f"{self.upload.filename} — chunk {self.chunk_number}"
