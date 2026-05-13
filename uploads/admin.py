from django.contrib import admin
from .models import Upload, UploadChunk


class UploadChunkInline(admin.TabularInline):
    model = UploadChunk
    extra = 0
    readonly_fields = ('chunk_number', 'size', 'created_at')


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'progress_percentage', 'status', 'total_size', 'created_at')
    list_filter = ('status',)
    search_fields = ('filename', 'user__username')
    readonly_fields = ('upload_id', 'progress_percentage', 'created_at', 'updated_at')
    inlines = [UploadChunkInline]


@admin.register(UploadChunk)
class UploadChunkAdmin(admin.ModelAdmin):
    list_display = ('upload', 'chunk_number', 'size', 'created_at')
