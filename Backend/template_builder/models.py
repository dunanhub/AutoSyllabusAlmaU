import uuid

from django.conf import settings
from django.db import models


class SyllabusTemplate(models.Model):
    VALIDATION_VALID = 'valid'
    VALIDATION_INVALID = 'invalid'
    VALIDATION_CHOICES = [
        (VALIDATION_VALID, 'Valid'),
        (VALIDATION_INVALID, 'Invalid'),
    ]

    LANGUAGE_KZ = 'kz'
    LANGUAGE_RU = 'ru'
    LANGUAGE_EN = 'en'
    LANGUAGE_CHOICES = [
        (LANGUAGE_KZ, 'Kazakh'),
        (LANGUAGE_RU, 'Russian'),
        (LANGUAGE_EN, 'English'),
    ]

    TRANSLATION_NOT_TRANSLATED = 'not_translated'
    TRANSLATION_TRANSLATING = 'translating'
    TRANSLATION_COMPLETED = 'completed'
    TRANSLATION_FAILED = 'failed'
    TRANSLATION_CHOICES = [
        (TRANSLATION_NOT_TRANSLATED, 'Not translated'),
        (TRANSLATION_TRANSLATING, 'Translating'),
        (TRANSLATION_COMPLETED, 'Completed'),
        (TRANSLATION_FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='syllabus_templates')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    content = models.TextField(blank=True, default='')
    markers = models.JSONField(default=list, blank=True)
    validation_status = models.CharField(max_length=16, choices=VALIDATION_CHOICES, default=VALIDATION_INVALID)
    is_default = models.BooleanField(default=False)
    source_language = models.CharField(max_length=8, choices=LANGUAGE_CHOICES, default=LANGUAGE_RU)
    content_kz = models.TextField(blank=True, default='')
    content_ru = models.TextField(blank=True, default='')
    content_en = models.TextField(blank=True, default='')
    translation_status = models.CharField(
        max_length=24,
        choices=TRANSLATION_CHOICES,
        default=TRANSLATION_NOT_TRANSLATED,
    )
    translation_error = models.TextField(blank=True, default='')
    translated_at = models.DateTimeField(null=True, blank=True)
    translation_task_id = models.CharField(max_length=255, blank=True, default='')
    content_hash = models.CharField(max_length=64, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['owner'],
                condition=models.Q(is_default=True),
                name='unique_default_syllabus_template_per_owner',
            )
        ]

    def __str__(self):
        return self.title
