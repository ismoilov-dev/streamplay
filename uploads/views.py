import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiTypes, OpenApiParameter
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .models import Upload, UploadChunk
from .serializers import (
    UploadSerializer, InitiateUploadSerializer, UploadChunkSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['uploads']),
    retrieve=extend_schema(tags=['uploads']),
    destroy=extend_schema(tags=['uploads']),
    initiate=extend_schema(tags=['uploads'], request=InitiateUploadSerializer, responses=UploadSerializer),
    upload_chunk=extend_schema(
        tags=['uploads'],
        request={'multipart/form-data': {
            'type': 'object',
            'properties': {
                'chunk_number': {'type': 'integer'},
                'file': {'type': 'string', 'format': 'binary'},
            },
            'required': ['chunk_number', 'file'],
        }},
        responses=UploadSerializer,
    ),
    complete=extend_schema(tags=['uploads'], responses=UploadSerializer),
    status_check=extend_schema(tags=['uploads'], responses=UploadSerializer),
    cancel=extend_schema(tags=['uploads']),
)
class UploadViewSet(viewsets.ModelViewSet):
    """
    Chunked (bo'laklab) fayl yuklash — Tus Protocol soddalashtirilgan versiyasi.

    Workflow:
    1. POST /api/uploads/initiate/     — sessiya ochish
    2. POST /api/uploads/{id}/chunk/   — har bir bo'lakni yuborish
    3. POST /api/uploads/{id}/complete/ — barcha bo'laklarni birlashtirish
    4. GET  /api/uploads/{id}/status/  — yuklash holatini tekshirish
    """
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    lookup_field = 'upload_id'
    lookup_url_kwarg = 'upload_id'
    lookup_value_regex = '[0-9a-f-]{36}'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Upload.objects.none()
        user = self.request.user
        if user.is_staff:
            return Upload.objects.all().prefetch_related('chunks')
        return Upload.objects.filter(user=user).prefetch_related('chunks')

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """1-qadam: Yangi yuklash sessiyasi ochish."""
        serializer = InitiateUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        upload = Upload.objects.create(
            user=request.user,
            filename=data['filename'],
            total_size=data['total_size'],
            content_type=data.get('content_type', ''),
            metadata=data.get('metadata', {}),
        )
        return Response(
            {
                'message': 'Yuklash sessiyasi ochildi.',
                'upload': UploadSerializer(upload).data,
                'next_step': f'/api/uploads/{upload.upload_id}/chunk/',
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='chunk',
            parser_classes=[MultiPartParser, FormParser])
    def upload_chunk(self, request, upload_id=None):
        """2-qadam: Bitta bo'lakni (chunk) yuklash."""
        upload = self.get_object()

        if upload.status not in ('in_progress',):
            return Response(
                {'error': f"Bu sessiyaga yuklash mumkin emas (status: {upload.status})."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chunk_number = request.data.get('chunk_number')
        chunk_file = request.FILES.get('file')

        if chunk_number is None:
            return Response({'chunk_number': 'Majburiy maydon.'}, status=status.HTTP_400_BAD_REQUEST)
        if not chunk_file:
            return Response({'file': 'Majburiy maydon.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            chunk_number = int(chunk_number)
        except (TypeError, ValueError):
            return Response({'chunk_number': 'Raqam bo\'lishi kerak.'}, status=status.HTTP_400_BAD_REQUEST)

        # Takroriy chunk bo'lsa — yangilaymiz (resume uchun)
        chunk_size = chunk_file.size
        with transaction.atomic():
            existing = UploadChunk.objects.filter(upload=upload, chunk_number=chunk_number).first()
            if existing:
                # hajmini qayta hisoblaymiz
                upload.uploaded_bytes = max(0, upload.uploaded_bytes - existing.size)
                existing.file.delete(save=False)
                existing.file = chunk_file
                existing.size = chunk_size
                existing.save()
            else:
                UploadChunk.objects.create(
                    upload=upload,
                    chunk_number=chunk_number,
                    file=chunk_file,
                    size=chunk_size,
                )
            upload.uploaded_bytes += chunk_size
            if upload.uploaded_bytes > upload.total_size:
                upload.uploaded_bytes = upload.total_size
            upload.save(update_fields=['uploaded_bytes', 'updated_at'])

        return Response({
            'message': f"Chunk {chunk_number} qabul qilindi.",
            'upload': UploadSerializer(upload).data,
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, upload_id=None):
        """3-qadam: Barcha chunklarni birlashtirish."""
        upload = self.get_object()

        if upload.status == 'completed':
            return Response({
                'message': 'Allaqachon tugallangan.',
                'upload': UploadSerializer(upload).data,
            })

        chunks = upload.chunks.order_by('chunk_number')
        if not chunks.exists():
            return Response(
                {'error': 'Hech qanday chunk yuklanmagan.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Chunklarni birlashtirish
        final_dir = os.path.join(settings.MEDIA_ROOT, f'uploads/final/{upload.upload_id}')
        os.makedirs(final_dir, exist_ok=True)
        final_path = os.path.join(final_dir, upload.filename)

        try:
            with open(final_path, 'wb') as final_file:
                for chunk in chunks:
                    chunk.file.open('rb')
                    try:
                        for part in chunk.file.chunks():
                            final_file.write(part)
                    finally:
                        chunk.file.close()
        except OSError as exc:
            upload.status = 'failed'
            upload.save(update_fields=['status', 'updated_at'])
            return Response(
                {'error': f"Birlashtirishda xatolik: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Modelga relative path saqlaymiz
        relative_path = os.path.relpath(final_path, settings.MEDIA_ROOT)
        upload.final_file.name = relative_path
        upload.status = 'completed'
        upload.uploaded_bytes = os.path.getsize(final_path)
        upload.save(update_fields=['final_file', 'status', 'uploaded_bytes', 'updated_at'])

        return Response({
            'message': 'Yuklash muvaffaqiyatli tugallandi.',
            'upload': UploadSerializer(upload).data,
        })

    @action(detail=True, methods=['get'], url_path='status')
    def status_check(self, request, upload_id=None):
        """Yuklash holatini tekshirish (resume uchun)."""
        upload = self.get_object()
        uploaded_chunks = list(
            upload.chunks.order_by('chunk_number').values_list('chunk_number', flat=True)
        )
        return Response({
            'upload': UploadSerializer(upload).data,
            'uploaded_chunks': uploaded_chunks,
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, upload_id=None):
        """Yuklashni bekor qilish va chunklarni o'chirish."""
        upload = self.get_object()
        for chunk in upload.chunks.all():
            chunk.file.delete(save=False)
            chunk.delete()
        upload.status = 'cancelled'
        upload.save(update_fields=['status', 'updated_at'])
        return Response({'message': 'Yuklash bekor qilindi.'})
