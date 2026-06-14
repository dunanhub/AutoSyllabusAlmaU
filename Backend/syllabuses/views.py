import re
import uuid

from django.core.cache import cache
from django.http import FileResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Syllabus
from .cache import CACHE_TIMEOUT, invalidate_syllabus_cache, syllabus_cache_key
from .permissions import IsOwnerOrAdmin
from .serializers import SyllabusSerializer
from .tasks import generate_syllabus_pdf_task


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
        invalidate_syllabus_cache()
        try:
            generate_syllabus_pdf_task.apply_async(args=[str(syllabus.id)], task_id=task_id)
        except Exception as error:
            syllabus.pdf_status = Syllabus.PDF_STATUS_FAILED
            syllabus.pdf_error = str(error)
            syllabus.save(update_fields=['pdf_status', 'pdf_error'])
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
        return Response({
            'taskId': syllabus.pdf_task_id,
            'pdfStatus': syllabus.pdf_status,
            'pdfGeneratedAt': syllabus.pdf_generated_at,
            'pdfError': syllabus.pdf_error,
            'pdfFile': pdf_file,
        })

    @extend_schema(
        responses={
            (200, 'application/pdf'): OpenApiTypes.BINARY,
            400: OpenApiResponse(description='PDF is not generated yet'),
        },
    )
    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, id=None):
        syllabus = self.get_object()
        if (
            syllabus.pdf_status != Syllabus.PDF_STATUS_GENERATED
            or not syllabus.pdf_file
            or not syllabus.pdf_file.storage.exists(syllabus.pdf_file.name)
        ):
            return Response(
                {'detail': 'PDF is not generated yet'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course_code = ''
        if hasattr(syllabus, 'titleInfo'):
            course_code = syllabus.titleInfo.codeAndName.split('—', 1)[0].strip()
        safe_code = re.sub(r'[^\w.-]+', '_', course_code, flags=re.UNICODE).strip('._')
        filename = f'syllabus_{safe_code or syllabus.id}.pdf'
        return FileResponse(
            syllabus.pdf_file.open('rb'),
            as_attachment=True,
            filename=filename,
            content_type='application/pdf',
        )
