import uuid

from django.conf import settings
from django.db import models


class CeleryTaskLog(models.Model):
    STATUS_QUEUED = 'queued'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_QUEUED, 'Queued'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    TYPE_TEMPLATE_TRANSLATION = 'template_translation'
    TYPE_SYLLABUS_AI_FILL = 'syllabus_ai_fill'
    TYPE_RENDER_TRANSLATION = 'render_translation'
    TYPE_DOCUMENT_GENERATION = 'document_generation'
    TYPE_CHOICES = [
        (TYPE_TEMPLATE_TRANSLATION, 'Template translation'),
        (TYPE_SYLLABUS_AI_FILL, 'Syllabus AI fill'),
        (TYPE_RENDER_TRANSLATION, 'Rendered syllabus translation'),
        (TYPE_DOCUMENT_GENERATION, 'Document generation'),
    ]

    ACTION_TEMPLATE_TRANSLATE = 'template_translate'
    ACTION_SYLLABUS_AI_FILL = 'syllabus_ai_fill'
    ACTION_SYLLABUS_RENDER_TRANSLATE = 'syllabus_render_translate'
    ACTION_SYLLABUS_DOCUMENTS = 'syllabus_documents'
    ACTION_CHOICES = [
        (ACTION_TEMPLATE_TRANSLATE, 'Retry template translation'),
        (ACTION_SYLLABUS_AI_FILL, 'Retry syllabus AI fill'),
        (ACTION_SYLLABUS_RENDER_TRANSLATE, 'Retry rendered translation'),
        (ACTION_SYLLABUS_DOCUMENTS, 'Retry documents generation'),
    ]

    OBJECT_TEMPLATE = 'template'
    OBJECT_SYLLABUS = 'syllabus'
    OBJECT_CHOICES = [
        (OBJECT_TEMPLATE, 'Template'),
        (OBJECT_SYLLABUS, 'Syllabus'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='celery_task_logs')
    task_id = models.CharField(max_length=255, db_index=True)
    task_type = models.CharField(max_length=64, choices=TYPE_CHOICES)
    object_type = models.CharField(max_length=32, choices=OBJECT_CHOICES)
    object_id = models.CharField(max_length=64, db_index=True)
    object_title = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_QUEUED)
    retry_action = models.CharField(max_length=64, choices=ACTION_CHOICES)
    error = models.TextField(blank=True, default='')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['owner', 'task_type']),
            models.Index(fields=['owner', 'created_at']),
        ]

    def __str__(self):
        return f'{self.task_type}:{self.task_id}'

