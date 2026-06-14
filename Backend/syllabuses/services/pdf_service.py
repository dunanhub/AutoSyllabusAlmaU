from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

from syllabuses.models import LiteratureItem, Syllabus


def _load_syllabus(syllabus_id):
    return (
        Syllabus.objects
        .select_related('owner', 'titleInfo', 'coursePolicy', 'signatures')
        .prefetch_related(
            'classSchedule',
            'learningOutcomes',
            'thematicPlan',
            'assessmentSystem',
            'literatureItems',
        )
        .get(id=syllabus_id)
    )


def generate_syllabus_pdf(syllabus) -> Syllabus:
    syllabus = _load_syllabus(syllabus.id)
    filename = f'syllabus_{syllabus.id}.pdf'
    old_file_name = syllabus.pdf_file.name if syllabus.pdf_file else ''
    storage = syllabus.pdf_file.storage

    try:
        literature_items = list(syllabus.literatureItems.all())
        context = {
            'syllabus': syllabus,
            'required_literature': [
                item for item in literature_items
                if item.type == LiteratureItem.TYPE_REQUIRED
            ],
            'additional_literature': [
                item for item in literature_items
                if item.type == LiteratureItem.TYPE_ADDITIONAL
            ],
            'internet_resources': [
                item for item in literature_items
                if item.type == LiteratureItem.TYPE_INTERNET
            ],
        }
        html = render_to_string('syllabuses/pdf/syllabus_pdf.html', context)
        pdf_bytes = HTML(string=html, base_url=str(settings.BASE_DIR)).write_pdf()

        if old_file_name:
            storage.delete(old_file_name)
        syllabus.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
        syllabus.pdf_status = Syllabus.PDF_STATUS_GENERATED
        syllabus.pdf_generated_at = timezone.now()
        syllabus.pdf_error = ''
        syllabus.save(update_fields=['pdf_file', 'pdf_status', 'pdf_generated_at', 'pdf_error'])
        return _load_syllabus(syllabus.id)
    except Exception as error:
        syllabus.pdf_status = Syllabus.PDF_STATUS_FAILED
        syllabus.pdf_generated_at = None
        syllabus.pdf_error = str(error)
        syllabus.save(update_fields=['pdf_status', 'pdf_generated_at', 'pdf_error'])
        raise
