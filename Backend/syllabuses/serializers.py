from django.db import transaction
from rest_framework import serializers

from .models import (
    AssessmentRow,
    ClassScheduleRow,
    CoursePolicy,
    LearningOutcomeRow,
    LiteratureItem,
    SignatureBlock,
    Syllabus,
    SyllabusTitleInfo,
    ThematicPlanRow,
)


class SyllabusTitleInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyllabusTitleInfo
        exclude = ['syllabus']


class ClassScheduleRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassScheduleRow
        exclude = ['syllabus']


class LearningOutcomeRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningOutcomeRow
        exclude = ['syllabus']


class ThematicPlanRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThematicPlanRow
        exclude = ['syllabus']


class AssessmentRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentRow
        exclude = ['syllabus']


class LiteratureItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiteratureItem
        exclude = ['syllabus']


class LiteratureBlockSerializer(serializers.Serializer):
    required = serializers.ListField(child=serializers.CharField(allow_blank=True), required=False)
    additional = serializers.ListField(child=serializers.CharField(allow_blank=True), required=False)
    internetResources = serializers.ListField(child=serializers.CharField(allow_blank=True), required=False)


class CoursePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePolicy
        exclude = ['syllabus']


class SignatureBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignatureBlock
        exclude = ['syllabus']


class SyllabusSerializer(serializers.ModelSerializer):
    titleInfo = SyllabusTitleInfoSerializer(required=False)
    classSchedule = ClassScheduleRowSerializer(many=True, required=False)
    learningOutcomes = LearningOutcomeRowSerializer(many=True, required=False)
    thematicPlan = ThematicPlanRowSerializer(many=True, required=False)
    assessmentSystem = AssessmentRowSerializer(many=True, required=False)
    literature = LiteratureBlockSerializer(required=False)
    coursePolicy = CoursePolicySerializer(required=False)
    signatures = SignatureBlockSerializer(required=False)
    pdfFile = serializers.FileField(source='pdf_file', read_only=True, allow_null=True)
    pdfFileRu = serializers.FileField(source='pdf_file_ru', read_only=True, allow_null=True)
    pdfFileKz = serializers.FileField(source='pdf_file_kz', read_only=True, allow_null=True)
    pdfFileEn = serializers.FileField(source='pdf_file_en', read_only=True, allow_null=True)
    docxFileRu = serializers.FileField(source='docx_file_ru', read_only=True, allow_null=True)
    docxFileKz = serializers.FileField(source='docx_file_kz', read_only=True, allow_null=True)
    docxFileEn = serializers.FileField(source='docx_file_en', read_only=True, allow_null=True)
    pdfStatus = serializers.CharField(source='pdf_status', read_only=True)
    pdfGeneratedAt = serializers.DateTimeField(source='pdf_generated_at', read_only=True, allow_null=True)
    pdfError = serializers.CharField(source='pdf_error', read_only=True)
    pdfTaskId = serializers.CharField(source='pdf_task_id', read_only=True)
    constructorSavedAt = serializers.DateTimeField(source='constructor_saved_at', required=False, allow_null=True)
    renderedContent = serializers.CharField(source='rendered_content', read_only=True)
    renderedContentKz = serializers.CharField(source='rendered_content_kz', read_only=True)
    renderedContentRu = serializers.CharField(source='rendered_content_ru', read_only=True)
    renderedContentEn = serializers.CharField(source='rendered_content_en', read_only=True)
    renderTranslationStatus = serializers.CharField(source='render_translation_status', read_only=True)
    renderTranslationError = serializers.CharField(source='render_translation_error', read_only=True)
    renderTranslatedAt = serializers.DateTimeField(source='render_translated_at', read_only=True, allow_null=True)
    renderTranslationTaskId = serializers.CharField(source='render_translation_task_id', read_only=True)
    aiFillStatus = serializers.CharField(source='ai_fill_status', read_only=True)
    aiFillError = serializers.CharField(source='ai_fill_error', read_only=True)
    aiFillTaskId = serializers.CharField(source='ai_fill_task_id', read_only=True)
    aiFilledAt = serializers.DateTimeField(source='ai_filled_at', read_only=True, allow_null=True)

    class Meta:
        model = Syllabus
        fields = [
            'id', 'owner', 'status', 'completion', 'courseDescription', 'courseGoal', 'teachingPhilosophy',
            'titleInfo', 'classSchedule', 'learningOutcomes', 'thematicPlan', 'assessmentSystem', 'literature',
            'coursePolicy', 'signatures', 'pdfFile', 'pdfFileRu', 'pdfFileKz', 'pdfFileEn',
            'docxFileRu', 'docxFileKz', 'docxFileEn', 'pdfStatus', 'pdfGeneratedAt', 'pdfError', 'pdfTaskId',
            'constructorSavedAt', 'renderedContent', 'renderedContentKz', 'renderedContentRu', 'renderedContentEn',
            'renderTranslationStatus', 'renderTranslationError', 'renderTranslatedAt', 'renderTranslationTaskId',
            'aiFillStatus', 'aiFillError', 'aiFillTaskId', 'aiFilledAt',
            'createdAt', 'updatedAt'
        ]
        read_only_fields = [
            'id', 'owner', 'pdfFile', 'pdfFileRu', 'pdfFileKz', 'pdfFileEn',
            'docxFileRu', 'docxFileKz', 'docxFileEn', 'pdfStatus', 'pdfGeneratedAt', 'pdfError', 'pdfTaskId',
            'renderedContent', 'renderedContentKz', 'renderedContentRu', 'renderedContentEn',
            'renderTranslationStatus', 'renderTranslationError', 'renderTranslatedAt', 'renderTranslationTaskId',
            'aiFillStatus', 'aiFillError', 'aiFillTaskId', 'aiFilledAt',
            'createdAt', 'updatedAt'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        items = instance.literatureItems.all().order_by('type', 'order')
        data['literature'] = {
            'required': [item.text for item in items if item.type == LiteratureItem.TYPE_REQUIRED],
            'additional': [item.text for item in items if item.type == LiteratureItem.TYPE_ADDITIONAL],
            'internetResources': [item.text for item in items if item.type == LiteratureItem.TYPE_INTERNET],
        }
        return data

    def _sync_children(self, instance, items, serializer_class, relation_name):
        getattr(instance, relation_name).all().delete()
        serializer = serializer_class(many=True)
        model_class = serializer.Meta.model
        for index, item in enumerate(items, start=1):
            model_class.objects.create(syllabus=instance, order=item.get('order', index), **item)

    @transaction.atomic
    def create(self, validated_data):
        nested = self._extract_nested(validated_data)
        owner = validated_data.pop('owner', self.context['request'].user)
        syllabus = Syllabus.objects.create(owner=owner, **validated_data)
        self._create_nested(syllabus, nested)
        return syllabus

    @transaction.atomic
    def update(self, instance, validated_data):
        nested = self._extract_nested(validated_data)
        missing = nested['missing']
        content_changed = any(
            nested[key] is not missing
            for key in [
                'titleInfo', 'classSchedule', 'learningOutcomes', 'thematicPlan',
                'assessmentSystem', 'literature', 'coursePolicy', 'signatures'
            ]
        ) or any(
            key in validated_data
            for key in ['courseDescription', 'courseGoal', 'teachingPhilosophy']
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._create_nested(instance, nested, replace=True)

        if content_changed:
            document_fields = [
                'pdf_file', 'pdf_file_ru', 'pdf_file_kz', 'pdf_file_en',
                'docx_file_ru', 'docx_file_kz', 'docx_file_en',
            ]
            old_files = [
                (getattr(instance, field).storage, getattr(instance, field).name)
                for field in document_fields
                if getattr(instance, field)
            ]
            instance.pdf_file = None
            instance.pdf_file_ru = None
            instance.pdf_file_kz = None
            instance.pdf_file_en = None
            instance.docx_file_ru = None
            instance.docx_file_kz = None
            instance.docx_file_en = None
            instance.pdf_status = Syllabus.PDF_STATUS_NOT_GENERATED
            instance.pdf_generated_at = None
            instance.pdf_error = ''
            instance.pdf_task_id = ''
            instance.rendered_content = ''
            instance.rendered_content_kz = ''
            instance.rendered_content_ru = ''
            instance.rendered_content_en = ''
            instance.render_translation_status = Syllabus.RENDER_TRANSLATION_NOT_TRANSLATED
            instance.render_translation_error = ''
            instance.render_translated_at = None
            instance.render_translation_task_id = ''
            instance.ai_fill_status = Syllabus.AI_FILL_NOT_STARTED
            instance.ai_fill_error = ''
            instance.ai_fill_task_id = ''
            instance.ai_filled_at = None
            instance.save(update_fields=[
                'pdf_file', 'pdf_file_ru', 'pdf_file_kz', 'pdf_file_en',
                'docx_file_ru', 'docx_file_kz', 'docx_file_en',
                'pdf_status', 'pdf_generated_at', 'pdf_error', 'pdf_task_id',
                'rendered_content', 'rendered_content_kz', 'rendered_content_ru', 'rendered_content_en',
                'render_translation_status', 'render_translation_error', 'render_translated_at',
                'render_translation_task_id', 'ai_fill_status', 'ai_fill_error', 'ai_fill_task_id',
                'ai_filled_at',
            ])
            for old_storage, old_file_name in old_files:
                transaction.on_commit(lambda storage=old_storage, name=old_file_name: storage.delete(name))

        return instance

    def _extract_nested(self, validated_data):
        missing = object()
        return {
            'missing': missing,
            'titleInfo': validated_data.pop('titleInfo', missing),
            'classSchedule': validated_data.pop('classSchedule', missing),
            'learningOutcomes': validated_data.pop('learningOutcomes', missing),
            'thematicPlan': validated_data.pop('thematicPlan', missing),
            'assessmentSystem': validated_data.pop('assessmentSystem', missing),
            'literature': validated_data.pop('literature', missing),
            'coursePolicy': validated_data.pop('coursePolicy', missing),
            'signatures': validated_data.pop('signatures', missing),
        }

    def _create_nested(self, syllabus, nested, replace=False):
        missing = nested['missing']

        if nested['titleInfo'] is not missing:
            SyllabusTitleInfo.objects.update_or_create(syllabus=syllabus, defaults=nested['titleInfo'])
        if nested['coursePolicy'] is not missing:
            CoursePolicy.objects.update_or_create(syllabus=syllabus, defaults=nested['coursePolicy'])
        if nested['signatures'] is not missing:
            SignatureBlock.objects.update_or_create(syllabus=syllabus, defaults=nested['signatures'])
        if nested['literature'] is not missing:
            LiteratureItem.objects.filter(syllabus=syllabus).delete()
            for key, item_type in [
                ('required', LiteratureItem.TYPE_REQUIRED),
                ('additional', LiteratureItem.TYPE_ADDITIONAL),
                ('internetResources', LiteratureItem.TYPE_INTERNET),
            ]:
                for index, text in enumerate(nested['literature'].get(key, []), start=1):
                    LiteratureItem.objects.create(syllabus=syllabus, type=item_type, order=index, text=text)

        mappings = [
            ('classSchedule', ClassScheduleRow),
            ('learningOutcomes', LearningOutcomeRow),
            ('thematicPlan', ThematicPlanRow),
            ('assessmentSystem', AssessmentRow),
        ]
        for key, model_class in mappings:
            if nested[key] is missing:
                continue
            if replace:
                getattr(syllabus, key).all().delete()
            for index, item in enumerate(nested[key], start=1):
                payload = dict(item)
                payload.pop('id', None)
                payload.pop('order', None)
                model_class.objects.create(syllabus=syllabus, order=item.get('order', index), **payload)
