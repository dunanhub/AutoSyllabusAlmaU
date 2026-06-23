import re
import uuid

from django.core.cache import cache
from django.http import FileResponse
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from analytics.models import CeleryTaskLog
from analytics.services import create_task_log, mark_task_failed, syllabus_title

from .models import Syllabus
from .cache import CACHE_TIMEOUT, invalidate_syllabus_cache, syllabus_cache_key
from .permissions import IsOwnerOrAdmin
from .serializers import SyllabusSerializer
from .services.ai_fill_service import has_empty_ai_fill_blocks
from .tasks import ai_fill_syllabus_task, generate_syllabus_pdf_task, translate_rendered_syllabus_task


DOCUMENT_LANGUAGES = {'ru', 'kz', 'en'}
DOCUMENT_FORMATS = {'pdf', 'docx'}
DOCX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


class SyllabusViewSet(viewsets.ModelViewSet):
    serializer_class = SyllabusSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        queryset = Syllabus.objects.all().select_related('owner', 'titleInfo', 'coursePolicy', 'signatures').prefetch_related(
            'classSchedule', 'learningOutcomes', 'thematicPlan', 'assessmentSystem', 'literatureItems'
        )
        return queryset if user.is_staff else queryset.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        invalidate_syllabus_cache()

    def perform_update(self, serializer):
        serializer.save()
        invalidate_syllabus_cache()

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_syllabus_cache()

    def list(self, request, *args, **kwargs):
        key = syllabus_cache_key(request.user.id, 'list', request.query_params.urlencode())
        cached = cache.get(key)
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, CACHE_TIMEOUT)
        return response

    def retrieve(self, request, *args, **kwargs):
        key = syllabus_cache_key(request.user.id, 'detail', kwargs.get(self.lookup_field))
        cached = cache.get(key)
        if cached is not None:
            return Response(cached)
        response = super().retrieve(request, *args, **kwargs)
        cache.set(key, response.data, CACHE_TIMEOUT)
        return response

    @action(detail=True, methods=['post'])
    def duplicate(self, request, id=None):
        syllabus = self.get_object()
        data = SyllabusSerializer(syllabus).data
        data['status'] = 'draft'
        data['completion'] = 0
        data['owner'] = request.user.id
        data['id'] = None
        for optional_section in ('titleInfo', 'coursePolicy', 'signatures'):
            if data.get(optional_section) is None:
                data.pop(optional_section, None)
        serializer = SyllabusSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        duplicate = serializer.save()
        invalidate_syllabus_cache()
        return Response(SyllabusSerializer(duplicate).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='set-status')
    def set_status(self, request, id=None):
        syllabus = self.get_object()
        new_status = request.data.get('status')
        if new_status not in {Syllabus.STATUS_DRAFT, Syllabus.STATUS_READY}:
            return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        syllabus.status = new_status
        syllabus.save(update_fields=['status', 'updatedAt'])
        invalidate_syllabus_cache()
        return Response(SyllabusSerializer(syllabus).data)

    @extend_schema(
        request=None,
        responses={
            202: OpenApiResponse(description='PDF generation task accepted'),
            500: OpenApiResponse(description='PDF generation failed'),
        },
    )
    @action(detail=True, methods=['post'], url_path='generate-pdf')
    def generate_pdf(self, request, id=None):
        syllabus = self.get_object()
        if (
            syllabus.pdf_status == Syllabus.PDF_STATUS_PROCESSING
            and syllabus.pdf_task_id
        ):
            return Response(
                {'taskId': syllabus.pdf_task_id, 'status': Syllabus.PDF_STATUS_PROCESSING},
                status=status.HTTP_202_ACCEPTED,
            )

        task_id = str(uuid.uuid4())
        syllabus.pdf_status = Syllabus.PDF_STATUS_PROCESSING
        syllabus.pdf_generated_at = None
        syllabus.pdf_error = ''
        syllabus.pdf_task_id = task_id
        syllabus.save(update_fields=['pdf_status', 'pdf_generated_at', 'pdf_error', 'pdf_task_id'])
        create_task_log(
            owner=syllabus.owner,
            task_id=task_id,
            task_type=CeleryTaskLog.TYPE_DOCUMENT_GENERATION,
            object_type=CeleryTaskLog.OBJECT_SYLLABUS,
            object_id=syllabus.id,
            object_title=syllabus_title(syllabus),
            retry_action=CeleryTaskLog.ACTION_SYLLABUS_DOCUMENTS,
        )
        invalidate_syllabus_cache()
        try:
            generate_syllabus_pdf_task.apply_async(args=[str(syllabus.id)], task_id=task_id)
        except Exception as error:
            syllabus.pdf_status = Syllabus.PDF_STATUS_FAILED
            syllabus.pdf_error = str(error)
            syllabus.save(update_fields=['pdf_status', 'pdf_error'])
            mark_task_failed(task_id, error)
            invalidate_syllabus_cache()
            return Response(
                {
                    'detail': 'PDF generation failed',
                    'pdfStatus': syllabus.pdf_status,
                    'pdfError': syllabus.pdf_error,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {'taskId': task_id, 'status': Syllabus.PDF_STATUS_PROCESSING},
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(
        responses={200: OpenApiResponse(description='Current PDF generation status')},
    )
    @action(detail=True, methods=['get'], url_path='pdf-status')
    def pdf_status(self, request, id=None):
        syllabus = self.get_object()
        pdf_file = None
        if syllabus.pdf_file:
            pdf_file = request.build_absolute_uri(syllabus.pdf_file.url)
        documents = {
            language: {
                document_format: self._document_file_exists(
                    getattr(syllabus, f'{document_format}_file_{language}')
                )
                for document_format in DOCUMENT_FORMATS
            }
            for language in DOCUMENT_LANGUAGES
        }
        return Response({
            'taskId': syllabus.pdf_task_id,
            'pdfStatus': syllabus.pdf_status,
            'pdfGeneratedAt': syllabus.pdf_generated_at,
            'pdfError': syllabus.pdf_error,
            'pdfFile': pdf_file,
            'documents': documents,
        })

    @extend_schema(
        request=None,
        responses={202: OpenApiResponse(description='Rendered syllabus translation task accepted')},
    )
    @action(detail=True, methods=['post'], url_path='translate-rendered')
    def translate_rendered(self, request, id=None):
        syllabus = self.get_object()
        if (
            syllabus.render_translation_status == Syllabus.RENDER_TRANSLATION_TRANSLATING
            and syllabus.render_translation_task_id
        ):
            return Response(
                {'taskId': syllabus.render_translation_task_id, 'status': syllabus.render_translation_status},
                status=status.HTTP_202_ACCEPTED,
            )

        task_id = str(uuid.uuid4())
        syllabus.render_translation_status = Syllabus.RENDER_TRANSLATION_TRANSLATING
        syllabus.render_translation_error = ''
        syllabus.render_translated_at = None
        syllabus.render_translation_task_id = task_id
        syllabus.save(update_fields=[
            'render_translation_status',
            'render_translation_error',
            'render_translated_at',
            'render_translation_task_id',
            'updatedAt',
        ])
        create_task_log(
            owner=syllabus.owner,
            task_id=task_id,
            task_type=CeleryTaskLog.TYPE_RENDER_TRANSLATION,
            object_type=CeleryTaskLog.OBJECT_SYLLABUS,
            object_id=syllabus.id,
            object_title=syllabus_title(syllabus),
            retry_action=CeleryTaskLog.ACTION_SYLLABUS_RENDER_TRANSLATE,
        )
        invalidate_syllabus_cache()
        try:
            translate_rendered_syllabus_task.apply_async(args=[str(syllabus.id)], task_id=task_id)
        except Exception as error:
            syllabus.render_translation_status = Syllabus.RENDER_TRANSLATION_FAILED
            syllabus.render_translation_error = str(error)
            syllabus.save(update_fields=['render_translation_status', 'render_translation_error', 'updatedAt'])
            mark_task_failed(task_id, error)
            invalidate_syllabus_cache()
        return Response({'taskId': task_id, 'status': syllabus.render_translation_status}, status=status.HTTP_202_ACCEPTED)

    @extend_schema(responses={200: OpenApiResponse(description='Current rendered syllabus translation status')})
    @action(detail=True, methods=['get'], url_path='render-translation-status')
    def render_translation_status(self, request, id=None):
        syllabus = self.get_object()
        return Response({
            'taskId': syllabus.render_translation_task_id,
            'status': syllabus.render_translation_status,
            'error': syllabus.render_translation_error,
            'translatedAt': syllabus.render_translated_at,
            'renderedContent': syllabus.rendered_content,
            'renderedContentKz': syllabus.rendered_content_kz,
            'renderedContentRu': syllabus.rendered_content_ru,
            'renderedContentEn': syllabus.rendered_content_en,
        })

    @extend_schema(
        request=None,
        responses={202: OpenApiResponse(description='AI fill task accepted')},
    )
    @action(detail=True, methods=['post'], url_path='ai-fill')
    def ai_fill(self, request, id=None):
        syllabus = self.get_object()
        if (
            syllabus.ai_fill_status == Syllabus.AI_FILL_PROCESSING
            and syllabus.ai_fill_task_id
        ):
            return Response(
                {'taskId': syllabus.ai_fill_task_id, 'status': syllabus.ai_fill_status},
                status=status.HTTP_202_ACCEPTED,
            )

        if not has_empty_ai_fill_blocks(syllabus):
            syllabus.ai_fill_status = Syllabus.AI_FILL_COMPLETED
            syllabus.ai_fill_error = ''
            syllabus.ai_fill_task_id = ''
            syllabus.ai_filled_at = syllabus.ai_filled_at or timezone.now()
            syllabus.save(update_fields=[
                'ai_fill_status',
                'ai_fill_error',
                'ai_fill_task_id',
                'ai_filled_at',
                'updatedAt',
            ])
            invalidate_syllabus_cache()
            return Response(
                {'taskId': '', 'status': syllabus.ai_fill_status},
                status=status.HTTP_200_OK,
            )

        task_id = str(uuid.uuid4())
        syllabus.ai_fill_status = Syllabus.AI_FILL_PROCESSING
        syllabus.ai_fill_error = ''
        syllabus.ai_fill_task_id = task_id
        syllabus.ai_filled_at = None
        syllabus.save(update_fields=[
            'ai_fill_status',
            'ai_fill_error',
            'ai_fill_task_id',
            'ai_filled_at',
            'updatedAt',
        ])
        create_task_log(
            owner=syllabus.owner,
            task_id=task_id,
            task_type=CeleryTaskLog.TYPE_SYLLABUS_AI_FILL,
            object_type=CeleryTaskLog.OBJECT_SYLLABUS,
            object_id=syllabus.id,
            object_title=syllabus_title(syllabus),
            retry_action=CeleryTaskLog.ACTION_SYLLABUS_AI_FILL,
        )
        invalidate_syllabus_cache()
        try:
            ai_fill_syllabus_task.apply_async(args=[str(syllabus.id)], task_id=task_id)
        except Exception as error:
            syllabus.ai_fill_status = Syllabus.AI_FILL_FAILED
            syllabus.ai_fill_error = str(error)
            syllabus.ai_fill_task_id = ''
            syllabus.save(update_fields=['ai_fill_status', 'ai_fill_error', 'ai_fill_task_id', 'updatedAt'])
            mark_task_failed(task_id, error)
            invalidate_syllabus_cache()
        return Response({'taskId': task_id, 'status': syllabus.ai_fill_status}, status=status.HTTP_202_ACCEPTED)

    @extend_schema(responses={200: OpenApiResponse(description='Current AI fill status')})
    @action(detail=True, methods=['get'], url_path='ai-fill-status')
    def ai_fill_status(self, request, id=None):
        syllabus = self.get_object()
        return Response({
            'taskId': syllabus.ai_fill_task_id,
            'status': syllabus.ai_fill_status,
            'error': syllabus.ai_fill_error,
            'filledAt': syllabus.ai_filled_at,
            'syllabus': SyllabusSerializer(syllabus, context={'request': request}).data,
        })

    @extend_schema(
        responses={
            (200, 'application/pdf'): OpenApiTypes.BINARY,
            400: OpenApiResponse(description='PDF is not generated yet'),
        },
    )
    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, id=None):
        language = request.query_params.get('language', 'ru').lower()
        return self._download_document_response(request, id, language, 'pdf')

    @extend_schema(
        parameters=[],
        responses={
            (200, 'application/pdf'): OpenApiTypes.BINARY,
            (200, DOCX_CONTENT_TYPE): OpenApiTypes.BINARY,
            400: OpenApiResponse(description='Document is not generated yet'),
        },
    )
    @action(detail=True, methods=['get'], url_path='download-document')
    def download_document(self, request, id=None):
        language = request.query_params.get('language', 'ru').lower()
        document_format = request.query_params.get('format', 'pdf').lower()
        return self._download_document_response(request, id, language, document_format)

    def _download_document_response(self, request, id, language, document_format):
        syllabus = self.get_object()
        if language not in DOCUMENT_LANGUAGES or document_format not in DOCUMENT_FORMATS:
            return Response(
                {'detail': 'Invalid language or document format'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        field_name = f'{document_format}_file_{language}'
        document_file = getattr(syllabus, field_name)
        if document_format == 'pdf' and language == 'ru' and not document_file:
            document_file = syllabus.pdf_file

        if (
            syllabus.pdf_status != Syllabus.PDF_STATUS_GENERATED
            or not document_file
            or not document_file.storage.exists(document_file.name)
        ):
            return Response(
                {
                    'detail': 'Document is not generated yet',
                    'pdfStatus': syllabus.pdf_status,
                    'missing': field_name,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        course_code = ''
        if hasattr(syllabus, 'titleInfo'):
            course_code = syllabus.titleInfo.codeAndName.split('—', 1)[0].strip()
        safe_code = re.sub(r'[^\w.-]+', '_', course_code, flags=re.UNICODE).strip('._')
        filename = f'syllabus_{safe_code or syllabus.id}_{language}.{document_format}'
        content_type = 'application/pdf' if document_format == 'pdf' else DOCX_CONTENT_TYPE
        return FileResponse(
            document_file.open('rb'),
            as_attachment=True,
            filename=filename,
            content_type=content_type,
        )

    @staticmethod
    def _document_file_exists(document_file):
        return bool(
            document_file
            and document_file.name
            and document_file.storage.exists(document_file.name)
        )
