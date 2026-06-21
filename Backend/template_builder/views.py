import hashlib
import uuid

from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SyllabusTemplate
from .serializers import (
    SyllabusTemplateSerializer,
    TemplateTranslateAcceptedSerializer,
    TemplateTranslationStatusSerializer,
)
from .tasks import translate_template_task


def content_hash(content: str) -> str:
    return hashlib.sha256((content or '').encode('utf-8')).hexdigest()


class SyllabusTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = SyllabusTemplateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        queryset = SyllabusTemplate.objects.all().select_related('owner')
        return queryset if user.is_staff else queryset.filter(owner=user)

    def perform_create(self, serializer):
        with transaction.atomic():
            template = serializer.save(owner=self.request.user)
            self._after_save(template, created=True)

    def perform_update(self, serializer):
        previous = self.get_object()
        previous_hash = previous.content_hash
        with transaction.atomic():
            template = serializer.save()
            self._after_save(template, content_changed=previous_hash != content_hash(template.content))

    def _after_save(self, template: SyllabusTemplate, created=False, content_changed=True):
        new_hash = content_hash(template.content)
        update_fields = ['content_hash', 'updated_at']
        template.content_hash = new_hash

        if template.validation_status == SyllabusTemplate.VALIDATION_VALID and (created or content_changed):
            template.translation_status = SyllabusTemplate.TRANSLATION_TRANSLATING
            template.translation_error = ''
            template.translated_at = None
            template.translation_task_id = str(uuid.uuid4())
            update_fields += ['translation_status', 'translation_error', 'translated_at', 'translation_task_id']
            template.save(update_fields=update_fields)
            try:
                translate_template_task.apply_async(args=[str(template.id)], task_id=template.translation_task_id)
            except Exception as error:
                template.translation_status = SyllabusTemplate.TRANSLATION_FAILED
                template.translation_error = str(error)
                template.save(update_fields=['translation_status', 'translation_error', 'updated_at'])
            return

        if template.validation_status != SyllabusTemplate.VALIDATION_VALID:
            template.translation_status = SyllabusTemplate.TRANSLATION_NOT_TRANSLATED
            template.translation_error = ''
            template.translation_task_id = ''
            update_fields += ['translation_status', 'translation_error', 'translation_task_id']

        template.save(update_fields=update_fields)

    @extend_schema(
        request=None,
        responses={200: SyllabusTemplateSerializer, 400: OpenApiResponse(description='Draft template cannot be default')},
    )
    @action(detail=True, methods=['post'], url_path='set-default')
    def set_default(self, request, id=None):
        template = self.get_object()
        if template.validation_status != SyllabusTemplate.VALIDATION_VALID:
            return Response({'detail': 'Draft template cannot be set as default.'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            SyllabusTemplate.objects.filter(owner=request.user, is_default=True).exclude(id=template.id).update(is_default=False)
            template.is_default = True
            template.save(update_fields=['is_default', 'updated_at'])
        return Response(SyllabusTemplateSerializer(template).data)

    @extend_schema(
        request=None,
        responses={202: TemplateTranslateAcceptedSerializer, 400: OpenApiResponse(description='Invalid template cannot be translated')},
    )
    @action(detail=True, methods=['post'], url_path='translate')
    def translate(self, request, id=None):
        template = self.get_object()
        if template.validation_status != SyllabusTemplate.VALIDATION_VALID:
            return Response({'detail': 'Only valid templates can be translated.'}, status=status.HTTP_400_BAD_REQUEST)
        if template.translation_status == SyllabusTemplate.TRANSLATION_TRANSLATING and template.translation_task_id:
            return Response({'taskId': template.translation_task_id, 'status': template.translation_status}, status=status.HTTP_202_ACCEPTED)

        template.translation_status = SyllabusTemplate.TRANSLATION_TRANSLATING
        template.translation_error = ''
        template.translated_at = None
        template.translation_task_id = str(uuid.uuid4())
        template.save(update_fields=['translation_status', 'translation_error', 'translated_at', 'translation_task_id', 'updated_at'])
        try:
            translate_template_task.apply_async(args=[str(template.id)], task_id=template.translation_task_id)
        except Exception as error:
            template.translation_status = SyllabusTemplate.TRANSLATION_FAILED
            template.translation_error = str(error)
            template.save(update_fields=['translation_status', 'translation_error', 'updated_at'])
            return Response(
                {'taskId': template.translation_task_id, 'status': template.translation_status},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response({'taskId': template.translation_task_id, 'status': template.translation_status}, status=status.HTTP_202_ACCEPTED)

    @extend_schema(responses={200: TemplateTranslationStatusSerializer})
    @action(detail=True, methods=['get'], url_path='translations')
    def translations(self, request, id=None):
        template = self.get_object()
        return Response({
            'id': template.id,
            'sourceLanguage': template.source_language,
            'translationStatus': template.translation_status,
            'translationError': template.translation_error,
            'translatedAt': template.translated_at,
            'translationTaskId': template.translation_task_id,
            'contentKz': template.content_kz,
            'contentRu': template.content_ru,
            'contentEn': template.content_en,
        })
