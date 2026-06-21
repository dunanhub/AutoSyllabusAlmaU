from rest_framework import serializers

from .marker_whitelist import SUPPORTED_TEMPLATE_MARKERS
from .models import SyllabusTemplate


class SyllabusTemplateSerializer(serializers.ModelSerializer):
    validationStatus = serializers.CharField(source='validation_status', required=False)
    isDefault = serializers.BooleanField(source='is_default', read_only=True)
    sourceLanguage = serializers.CharField(source='source_language', required=False)
    contentKz = serializers.CharField(source='content_kz', read_only=True)
    contentRu = serializers.CharField(source='content_ru', read_only=True)
    contentEn = serializers.CharField(source='content_en', read_only=True)
    translationStatus = serializers.CharField(source='translation_status', read_only=True)
    translationError = serializers.CharField(source='translation_error', read_only=True)
    translatedAt = serializers.DateTimeField(source='translated_at', read_only=True, allow_null=True)
    translationTaskId = serializers.CharField(source='translation_task_id', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = SyllabusTemplate
        fields = [
            'id', 'owner', 'title', 'description', 'content', 'markers', 'validationStatus',
            'isDefault', 'sourceLanguage', 'contentKz', 'contentRu', 'contentEn',
            'translationStatus', 'translationError', 'translatedAt', 'translationTaskId',
            'createdAt', 'updatedAt',
        ]
        read_only_fields = [
            'id', 'owner', 'contentKz', 'contentRu', 'contentEn', 'translationStatus',
            'translationError', 'translatedAt', 'translationTaskId', 'createdAt', 'updatedAt',
        ]

    def validate_sourceLanguage(self, value):
        value = (value or SyllabusTemplate.LANGUAGE_RU).lower()
        if value not in {SyllabusTemplate.LANGUAGE_KZ, SyllabusTemplate.LANGUAGE_RU, SyllabusTemplate.LANGUAGE_EN}:
            raise serializers.ValidationError('Unsupported source language.')
        return value

    def validate_validationStatus(self, value):
        value = value or SyllabusTemplate.VALIDATION_INVALID
        if value not in {SyllabusTemplate.VALIDATION_VALID, SyllabusTemplate.VALIDATION_INVALID}:
            raise serializers.ValidationError('Unsupported validation status.')
        return value

    def validate_markers(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Markers must be a list.')
        for marker in value:
            key = marker.get('key') if isinstance(marker, dict) else ''
            if key and key not in SUPPORTED_TEMPLATE_MARKERS:
                raise serializers.ValidationError(f'Unsupported marker key: {key}')
        return value


class TemplateTranslationStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    sourceLanguage = serializers.CharField()
    translationStatus = serializers.CharField()
    translationError = serializers.CharField(allow_blank=True)
    translatedAt = serializers.DateTimeField(allow_null=True)
    translationTaskId = serializers.CharField(allow_blank=True)
    contentKz = serializers.CharField(allow_blank=True)
    contentRu = serializers.CharField(allow_blank=True)
    contentEn = serializers.CharField(allow_blank=True)


class TemplateTranslateAcceptedSerializer(serializers.Serializer):
    taskId = serializers.CharField()
    status = serializers.CharField()
