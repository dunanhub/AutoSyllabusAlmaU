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
    pdfStatus = serializers.CharField(source='pdf_status', read_only=True)
    pdfGeneratedAt = serializers.DateTimeField(source='pdf_generated_at', read_only=True, allow_null=True)
    pdfError = serializers.CharField(source='pdf_error', read_only=True)
    pdfTaskId = serializers.CharField(source='pdf_task_id', read_only=True)

    class Meta:
        model = Syllabus
        fields = [
            'id', 'owner', 'status', 'completion', 'courseDescription', 'courseGoal', 'teachingPhilosophy',
            'titleInfo', 'classSchedule', 'learningOutcomes', 'thematicPlan', 'assessmentSystem', 'literature',
            'coursePolicy', 'signatures', 'pdfFile', 'pdfStatus', 'pdfGeneratedAt', 'pdfError', 'pdfTaskId',
            'createdAt', 'updatedAt'
        ]
        read_only_fields = [
            'id', 'owner', 'pdfFile', 'pdfStatus', 'pdfGeneratedAt', 'pdfError', 'pdfTaskId',
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
            old_file_name = instance.pdf_file.name if instance.pdf_file else ''
            old_storage = instance.pdf_file.storage if instance.pdf_file else None
            instance.pdf_file = None
            instance.pdf_status = Syllabus.PDF_STATUS_NOT_GENERATED
            instance.pdf_generated_at = None
            instance.pdf_error = ''
            instance.pdf_task_id = ''
            instance.save(update_fields=['pdf_file', 'pdf_status', 'pdf_generated_at', 'pdf_error', 'pdf_task_id'])
            if old_file_name and old_storage:
                transaction.on_commit(lambda: old_storage.delete(old_file_name))

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
                payload.pop('order', None)
                model_class.objects.create(syllabus=syllabus, order=item.get('order', index), **payload)
