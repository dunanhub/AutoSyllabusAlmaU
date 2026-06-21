from django.core.files.base import ContentFile
from django.utils import timezone
from weasyprint import HTML

from syllabuses.models import Syllabus
from syllabuses.services.docx_service import html_to_docx_bytes
from syllabuses.services.rendered_translation_service import get_selected_template, render_template_with_syllabus


LANGUAGES = ('ru', 'kz', 'en')


def _document_html(body_html, language):
    return f'''<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <style>
    @page {{ size: A4; margin: 18mm; }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    body {{
      font-family: Arial, "DejaVu Sans", "Liberation Sans", sans-serif;
      color: #111827;
      font-size: 12px;
      line-height: 1.45;
      background: #ffffff;
      overflow-wrap: anywhere;
    }}
    p {{ margin: 0 0 8px; white-space: normal; }}
    h1, h2, h3, h4 {{ margin: 12px 0 8px; line-height: 1.25; page-break-after: avoid; }}
    ul, ol {{ margin: 0 0 8px 20px; padding: 0; }}
    li {{ margin: 0 0 4px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      margin: 0 0 10px;
      page-break-inside: auto;
    }}
    thead {{ display: table-header-group; }}
    tr {{ page-break-inside: avoid; }}
    th, td {{
      border: 1px solid #cbd5e1;
      padding: 6px;
      vertical-align: top;
      overflow-wrap: anywhere;
      word-break: break-word;
    }}
    img {{
      max-width: 100%;
      height: auto;
      object-fit: contain;
      page-break-inside: avoid;
    }}
    a {{ color: #2563eb; text-decoration: underline; }}
    .page-break, [data-page-break="true"] {{
      page-break-after: always;
      break-after: page;
      height: 0;
      margin: 0;
      padding: 0;
    }}
    .template-preview-marker,
    .template-empty-value {{
      color: #64748b;
      font-style: italic;
    }}
    .template-qr-code {{
      display: inline-block;
      line-height: 0;
      page-break-inside: avoid;
      break-inside: avoid;
    }}
    .template-qr-code img {{
      width: 96px;
      height: 96px;
      max-width: 96px;
      display: block;
    }}
  </style>
</head>
<body>{body_html or '<p>Не заполнено</p>'}</body>
</html>'''


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
    old_files = _document_file_names(syllabus)
    try:
        template = get_selected_template(syllabus)
        rendered_documents = {
            language: _render_document_body(syllabus, template, language)
            for language in LANGUAGES
        }

        for language in LANGUAGES:
            html = _document_html(rendered_documents[language], language)
            pdf_bytes = HTML(string=html).write_pdf()
            docx_bytes = html_to_docx_bytes(html)
            getattr(syllabus, f'pdf_file_{language}').save(
                f'syllabus_{syllabus.id}_{language}.pdf',
                ContentFile(pdf_bytes),
                save=False,
            )
            getattr(syllabus, f'docx_file_{language}').save(
                f'syllabus_{syllabus.id}_{language}.docx',
                ContentFile(docx_bytes),
                save=False,
            )

        if syllabus.pdf_file_ru:
            syllabus.pdf_file = syllabus.pdf_file_ru.name
        syllabus.rendered_content = rendered_documents['ru']
        syllabus.rendered_content_ru = rendered_documents['ru']
        syllabus.rendered_content_kz = rendered_documents['kz']
        syllabus.rendered_content_en = rendered_documents['en']
        syllabus.render_translation_status = Syllabus.RENDER_TRANSLATION_COMPLETED
        syllabus.render_translation_error = ''
        syllabus.render_translated_at = timezone.now()
        syllabus.pdf_status = Syllabus.PDF_STATUS_GENERATED
        syllabus.pdf_generated_at = timezone.now()
        syllabus.pdf_error = ''
        syllabus.save(update_fields=[
            'rendered_content', 'rendered_content_ru', 'rendered_content_kz', 'rendered_content_en',
            'render_translation_status', 'render_translation_error', 'render_translated_at',
            'pdf_file', 'pdf_file_ru', 'pdf_file_kz', 'pdf_file_en',
            'docx_file_ru', 'docx_file_kz', 'docx_file_en',
            'pdf_status', 'pdf_generated_at', 'pdf_error',
        ])
        _delete_files(syllabus, old_files)
        return _load_syllabus(syllabus.id)
    except Exception as error:
        syllabus.pdf_status = Syllabus.PDF_STATUS_FAILED
        syllabus.pdf_generated_at = None
        syllabus.pdf_error = str(error)
        syllabus.save(update_fields=['pdf_status', 'pdf_generated_at', 'pdf_error'])
        raise


def _document_file_names(syllabus):
    fields = ['pdf_file', *(f'pdf_file_{language}' for language in LANGUAGES), *(f'docx_file_{language}' for language in LANGUAGES)]
    return [
        (getattr(syllabus, field).storage, getattr(syllabus, field).name)
        for field in fields
        if getattr(syllabus, field)
    ]


def _render_document_body(syllabus, template, language):
    original_content = template.content
    try:
        template.content = getattr(template, f'content_{language}', '') or template.content or ''
        return render_template_with_syllabus(template, syllabus)
    finally:
        template.content = original_content


def _delete_files(syllabus, files):
    current = {name for _, name in _document_file_names(syllabus)}
    for storage, name in files:
        if name and name not in current:
            storage.delete(name)
