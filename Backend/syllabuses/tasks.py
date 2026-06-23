from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from analytics.services import mark_task_completed, mark_task_failed

from .cache import invalidate_syllabus_cache
from .models import Syllabus
from .services.ai_fill_service import ai_fill_syllabus
from .services.pdf_service import generate_syllabus_pdf
from .services.rendered_translation_service import translate_rendered_syllabus


@shared_task(bind=True)
def generate_syllabus_pdf_task(self, syllabus_id):
    try:
        syllabus = Syllabus.objects.get(id=syllabus_id)
        generate_syllabus_pdf(syllabus)
        mark_task_completed(self.request.id)
    except Exception as error:
        mark_task_failed(self.request.id, error)
        raise
    finally:
        invalidate_syllabus_cache()


@shared_task(bind=True)
def translate_rendered_syllabus_task(self, syllabus_id):
    try:
        translate_rendered_syllabus(syllabus_id)
        mark_task_completed(self.request.id)
    except Exception as error:
        mark_task_failed(self.request.id, error)
        raise
    finally:
        invalidate_syllabus_cache()


def _is_temporary_gemini_error(error):
    message = str(error)
    return '503' in message or 'UNAVAILABLE' in message or 'high demand' in message


@shared_task(bind=True, max_retries=3)
def ai_fill_syllabus_task(self, syllabus_id):
    try:
        ai_fill_syllabus(syllabus_id)
        mark_task_completed(self.request.id)
    except Exception as error:
        if _is_temporary_gemini_error(error):
            try:
                raise self.retry(exc=error, countdown=15 * (self.request.retries + 1))
            except MaxRetriesExceededError:
                pass

        syllabus = Syllabus.objects.get(id=syllabus_id)
        syllabus.ai_fill_status = Syllabus.AI_FILL_FAILED
        syllabus.ai_fill_error = str(error)
        syllabus.ai_fill_task_id = ''
        syllabus.save(update_fields=['ai_fill_status', 'ai_fill_error', 'ai_fill_task_id', 'updatedAt'])
        mark_task_failed(self.request.id, error)
        raise
    finally:
        invalidate_syllabus_cache()
