from rest_framework import serializers
from .models import Upload, UploadChunk


class UploadSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Upload
        fields = [
            'id', 'upload_id', 'user', 'filename', 'content_type',
            'total_size', 'uploaded_bytes', 'progress_percentage',
            'status', 'final_file', 'metadata',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'upload_id', 'user', 'uploaded_bytes', 'progress_percentage',
            'status', 'final_file', 'created_at', 'updated_at',
        ]


class InitiateUploadSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=500)
    total_size = serializers.IntegerField(min_value=1)
    content_type = serializers.CharField(max_length=200, required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)


class UploadChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadChunk
        fields = ['id', 'upload', 'chunk_number', 'file', 'size', 'created_at']
        read_only_fields = ['id', 'created_at']
