from celery import shared_task
from django.utils import timezone

from analytics.services import mark_task_completed, mark_task_failed

from .models import SyllabusTemplate
from .services.translation_service import TemplateTranslationService


TRANSIENT_TRANSLATION_ERRORS = (
    '503',
    'UNAVAILABLE',
    'high demand',
    'temporarily',
    'try again later',
)


def is_transient_translation_error(error: Exception) -> bool:
    message = str(error).lower()
    return any(token.lower() in message for token in TRANSIENT_TRANSLATION_ERRORS)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def translate_template_task(self, template_id):
    template = SyllabusTemplate.objects.get(id=template_id)
    try:
        template.translation_status = SyllabusTemplate.TRANSLATION_TRANSLATING
        template.translation_error = ''
        template.translation_task_id = self.request.id or template.translation_task_id
        template.save(update_fields=['translation_status', 'translation_error', 'translation_task_id', 'updated_at'])

        translated = TemplateTranslationService().translate_template(template)
        template.content_kz = translated[SyllabusTemplate.LANGUAGE_KZ]
        template.content_ru = translated[SyllabusTemplate.LANGUAGE_RU]
        template.content_en = translated[SyllabusTemplate.LANGUAGE_EN]
        template.translation_status = SyllabusTemplate.TRANSLATION_COMPLETED
        template.translation_error = ''
        template.translated_at = timezone.now()
        template.save(update_fields=[
            'content_kz', 'content_ru', 'content_en', 'translation_status',
            'translation_error', 'translated_at', 'updated_at',
        ])
        mark_task_completed(self.request.id)
    except Exception as error:
        if is_transient_translation_error(error) and self.request.retries < self.max_retries:
            template.translation_status = SyllabusTemplate.TRANSLATION_TRANSLATING
            template.translation_error = (
                'Gemini временно перегружен. Повторная попытка перевода будет выполнена автоматически.'
            )
            template.save(update_fields=['translation_status', 'translation_error', 'updated_at'])
            raise self.retry(exc=error, countdown=30 * (self.request.retries + 1))

        template.translation_status = SyllabusTemplate.TRANSLATION_FAILED
        template.translation_error = str(error)
        template.save(update_fields=['translation_status', 'translation_error', 'updated_at'])
        mark_task_failed(self.request.id, error)
        raise
