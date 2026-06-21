from celery import shared_task
from django.utils import timezone

from .models import SyllabusTemplate
from .services.translation_service import TemplateTranslationService


@shared_task(bind=True)
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
    except Exception as error:
        template.translation_status = SyllabusTemplate.TRANSLATION_FAILED
        template.translation_error = str(error)
        template.save(update_fields=['translation_status', 'translation_error', 'updated_at'])
        raise
