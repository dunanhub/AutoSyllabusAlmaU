from celery import shared_task

from .cache import invalidate_syllabus_cache
from .models import Syllabus
from .services.pdf_service import generate_syllabus_pdf


@shared_task(bind=True)
def generate_syllabus_pdf_task(self, syllabus_id):
    try:
        syllabus = Syllabus.objects.get(id=syllabus_id)
        generate_syllabus_pdf(syllabus)
    finally:
        invalidate_syllabus_cache()
