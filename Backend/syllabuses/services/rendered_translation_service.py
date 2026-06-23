import base64
import re
import uuid
from io import BytesIO
from html import escape

from django.utils import timezone
import qrcode

from template_builder.models import SyllabusTemplate
from template_builder.services.translation_service import TemplateTranslationService

from ..cache import invalidate_syllabus_cache
from ..models import Syllabus


TOKEN_RE = re.compile(r'\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}')
MARKER_SPAN_RE = re.compile(
    r'<span\b(?=[^>]*data-template-marker=["\']true["\'])(?=[^>]*data-marker-key=["\']([^"\']+)["\'])[^>]*>.*?</span>',
    re.IGNORECASE | re.DOTALL,
)


def get_syllabus_for_render(syllabus_id):
    return Syllabus.objects.select_related(
        'owner',
        'titleInfo',
        'coursePolicy',
        'signatures',
    ).prefetch_related(
        'classSchedule',
        'learningOutcomes',
        'thematicPlan',
        'assessmentSystem',
        'literatureItems',
    ).get(id=syllabus_id)


def get_selected_template(syllabus: Syllabus) -> SyllabusTemplate:
    template_id = getattr(getattr(syllabus, 'titleInfo', None), 'templateId', '') or ''
    queryset = SyllabusTemplate.objects.filter(owner=syllabus.owner, validation_status=SyllabusTemplate.VALIDATION_VALID)
    if template_id:
        try:
            template_uuid = uuid.UUID(str(template_id))
        except (TypeError, ValueError):
            template_uuid = None
        if template_uuid:
            template = queryset.filter(id=template_uuid).first()
            if template:
                return template
    template = queryset.filter(is_default=True).first() or queryset.first()
    if not template:
        raise ValueError('No valid syllabus template is available for rendered preview translation.')
    return template


def render_template_with_syllabus(template: SyllabusTemplate, syllabus: Syllabus) -> str:
    content = template.content or ''
    rendered = MARKER_SPAN_RE.sub(lambda match: resolve_marker_html(match.group(1), syllabus), content)
    rendered = TOKEN_RE.sub(lambda match: resolve_marker_html(match.group(1), syllabus), rendered)
    return rendered


def translate_rendered_syllabus(syllabus_id):
    syllabus = get_syllabus_for_render(syllabus_id)
    template = get_selected_template(syllabus)
    source_html = render_template_with_syllabus(template, syllabus)
    service = TemplateTranslationService()
    source_language = template.source_language or SyllabusTemplate.LANGUAGE_RU

    try:
        syllabus.rendered_content = source_html
        syllabus.rendered_content_kz = service.translate_to_kz(source_html, source_language)
        syllabus.rendered_content_ru = service.translate_to_ru(source_html, source_language)
        syllabus.rendered_content_en = service.translate_to_en(source_html, source_language)
        syllabus.render_translation_status = Syllabus.RENDER_TRANSLATION_COMPLETED
        syllabus.render_translation_error = ''
        syllabus.render_translated_at = timezone.now()
        syllabus.save(update_fields=[
            'rendered_content',
            'rendered_content_kz',
            'rendered_content_ru',
            'rendered_content_en',
            'render_translation_status',
            'render_translation_error',
            'render_translated_at',
            'updatedAt',
        ])
    except Exception as error:
        syllabus.rendered_content = source_html
        syllabus.render_translation_status = Syllabus.RENDER_TRANSLATION_FAILED
        syllabus.render_translation_error = str(error)
        syllabus.render_translated_at = None
        syllabus.save(update_fields=[
            'rendered_content',
            'render_translation_status',
            'render_translation_error',
            'render_translated_at',
            'updatedAt',
        ])
        raise
    finally:
        invalidate_syllabus_cache()

    return syllabus


def resolve_marker_html(key: str, syllabus: Syllabus) -> str:
    title = getattr(syllabus, 'titleInfo', None)
    policy = getattr(syllabus, 'coursePolicy', None)
    signatures = getattr(syllabus, 'signatures', None)
    syllabus_url = getattr(title, 'qrUrl', '') if title else ''
    text_values = {
        'course.code_and_name': getattr(title, 'codeAndName', ''),
        'course.credits': getattr(title, 'credits', ''),
        'course.total_hours': getattr(title, 'totalHours', ''),
        'course.classroom_hours': getattr(title, 'classroomHours', ''),
        'course.independent_hours': getattr(title, 'independentWorkHours', ''),
        'course.prerequisites': getattr(title, 'prerequisites', ''),
        'course.level': getattr(title, 'levelOfTraining', ''),
        'course.semester': getattr(title, 'semester', ''),
        'course.program': getattr(title, 'educationalProgram', ''),
        'course.format': getattr(title, 'formatOfTraining', ''),
        'course.time_place': getattr(title, 'timeAndPlace', ''),
        'teacher.full_name': getattr(title, 'instructorName', ''),
        'teacher.email': getattr(title, 'instructorEmail', ''),
        'manual.course_description': syllabus.courseDescription,
        'manual.course_goal': syllabus.courseGoal,
        'manual.teaching_methods': getattr(policy, 'masteringDiscipline', '') or getattr(policy, 'informationCommunication', ''),
        'manual.teaching_philosophy': syllabus.teachingPhilosophy,
        'approval.director_name': getattr(signatures, 'preparedByName', ''),
        'approval.program_leader': getattr(signatures, 'preparedByPosition', ''),
        'syllabus.url': syllabus_url,
    }

    if key in text_values:
        return escape(str(text_values[key] or 'Не заполнено'), quote=False)
    if key == 'syllabus.qr':
        return render_qr_code(syllabus_url)
    if key == 'list.required_literature':
        return render_list([item.text for item in syllabus.literatureItems.all() if item.type == 'required'])
    if key == 'list.additional_literature':
        return render_list([item.text for item in syllabus.literatureItems.all() if item.type == 'additional'])
    if key == 'list.internet_resources':
        return render_list([item.text for item in syllabus.literatureItems.all() if item.type == 'internet'])
    if key == 'table.learning_outcomes':
        return render_table(
            ['Код', 'Результат курса', 'Результат программы', 'Описание'],
            [[row.code, row.courseLearningOutcome, row.programLearningOutcome, row.description] for row in syllabus.learningOutcomes.all()],
        )
    if key == 'table.weekly_plan':
        return render_table(
            ['Неделя', 'Модуль', 'Результат', 'Вопросы', 'Задания'],
            [[row.week, row.topicModule, row.courseOutcome, row.questions, row.tasks] for row in syllabus.thematicPlan.all()],
        )
    if key == 'table.rubric':
        return render_table(
            ['Компонент', 'Макс. %', 'Вес', 'Итоговые баллы'],
            [[row.topicModule, row.maxPercent, row.maxWeight, row.finalPoints] for row in syllabus.assessmentSystem.all()],
        )
    return '<span class="template-empty-value">Не заполнено</span>'


def render_list(items):
    values = [item for item in items if str(item or '').strip()]
    if not values:
        return '<span class="template-empty-value">Не заполнено</span>'
    return '<ol>' + ''.join(f'<li>{escape(str(item), quote=False)}</li>' for item in values) + '</ol>'


def render_table(headers, rows):
    rows = [row for row in rows if any(str(cell or '').strip() for cell in row)]
    if not rows:
        return '<span class="template-empty-value">Не заполнено</span>'
    head = ''.join(f'<th>{escape(str(header), quote=False)}</th>' for header in headers)
    body = ''.join(
        '<tr>' + ''.join(f'<td>{escape(str(cell or ""), quote=False)}</td>' for cell in row) + '</tr>'
        for row in rows
    )
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def render_qr_code(value: str) -> str:
    value = str(value or '').strip()
    if not value:
        return '<span class="template-empty-value">Не заполнено</span>'

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=3,
    )
    qr.add_data(value)
    qr.make(fit=True)
    image = qr.make_image(fill_color='black', back_color='white').convert('RGB')
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    data_uri = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')
    safe_value = escape(value, quote=True)
    return (
        '<span class="template-qr-code" data-template-rendered-qr="true">'
        f'<img src="{data_uri}" alt="QR code" title="{safe_value}" '
        'style="width:96px;height:96px;display:block;object-fit:contain;" />'
        '</span>'
    )
