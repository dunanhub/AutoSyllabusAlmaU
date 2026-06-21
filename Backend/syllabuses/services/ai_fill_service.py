import json
import re

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from ..models import (
    AssessmentRow,
    CoursePolicy,
    LearningOutcomeRow,
    LiteratureItem,
    Syllabus,
    ThematicPlanRow,
)


def ai_fill_syllabus(syllabus_id):
    syllabus = get_syllabus_for_ai_fill(syllabus_id)
    payload = _call_gemini_for_syllabus(syllabus)
    with transaction.atomic():
        syllabus = get_syllabus_for_ai_fill(syllabus_id, for_update=True)
        _apply_ai_payload(syllabus, payload)
        _ensure_minimum_weekly_plan(syllabus, payload.get('weekly_plan', []))
        syllabus.ai_fill_status = Syllabus.AI_FILL_COMPLETED
        syllabus.ai_fill_error = ''
        syllabus.ai_filled_at = timezone.now()
        syllabus.save(update_fields=['ai_fill_status', 'ai_fill_error', 'ai_filled_at', 'updatedAt'])
    return syllabus


def get_syllabus_for_ai_fill(syllabus_id, for_update=False):
    if for_update:
        return Syllabus.objects.select_for_update().get(id=syllabus_id)

    queryset = Syllabus.objects.select_related('titleInfo', 'coursePolicy', 'signatures').prefetch_related(
        'learningOutcomes',
        'thematicPlan',
        'assessmentSystem',
        'literatureItems',
    )
    return queryset.get(id=syllabus_id)


def has_empty_ai_fill_blocks(syllabus):
    policy, _ = CoursePolicy.objects.get_or_create(syllabus=syllabus)
    return any([
        _blank(syllabus.courseGoal),
        _blank(policy.masteringDiscipline),
        _blank(syllabus.teachingPhilosophy),
        _rows_empty(
            syllabus.learningOutcomes.all(),
            ['code', 'courseLearningOutcome', 'programLearningOutcome', 'description'],
        ),
        syllabus.thematicPlan.count() < 16 or _rows_empty(
            syllabus.thematicPlan.all(),
            ['topicModule', 'courseOutcome', 'questions', 'tasks', 'literature', 'gradeStructure'],
        ),
        _rows_empty(syllabus.assessmentSystem.all(), ['topicModule', 'maxPercent', 'maxWeight', 'finalPoints']),
        not LiteratureItem.objects.filter(
            syllabus=syllabus,
            type=LiteratureItem.TYPE_REQUIRED,
        ).exclude(text='').exists(),
        not LiteratureItem.objects.filter(
            syllabus=syllabus,
            type=LiteratureItem.TYPE_ADDITIONAL,
        ).exclude(text='').exists(),
        not LiteratureItem.objects.filter(
            syllabus=syllabus,
            type=LiteratureItem.TYPE_INTERNET,
        ).exclude(text='').exists(),
    ])


def _call_gemini_for_syllabus(syllabus):
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        raise RuntimeError('GEMINI_API_KEY is not configured.')

    try:
        from google import genai
        from google.genai import types
    except ImportError as error:
        raise RuntimeError('google-genai package is not installed.') from error

    model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
    prompt = _build_prompt(syllabus)
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type='application/json'),
    )
    return _parse_json_response(getattr(response, 'text', '') or '')


def _build_prompt(syllabus):
    title = getattr(syllabus, 'titleInfo', None)
    course = {
        'codeAndName': getattr(title, 'codeAndName', ''),
        'credits': getattr(title, 'credits', ''),
        'totalHours': getattr(title, 'totalHours', ''),
        'classroomHours': getattr(title, 'classroomHours', ''),
        'independentWorkHours': getattr(title, 'independentWorkHours', ''),
        'prerequisites': getattr(title, 'prerequisites', ''),
        'levelOfTraining': getattr(title, 'levelOfTraining', ''),
        'semester': getattr(title, 'semester', ''),
        'educationalProgram': getattr(title, 'educationalProgram', ''),
        'formatOfTraining': getattr(title, 'formatOfTraining', ''),
        'timeAndPlace': getattr(title, 'timeAndPlace', ''),
        'courseDescription': syllabus.courseDescription,
    }
    return (
        'You are helping an AlmaU instructor complete a university syllabus. '
        'Generate concise, academically appropriate Russian content from the course data. '
        'Return only valid JSON. Do not add markdown fences or explanations. '
        'Never include null values; use empty strings if needed. '
        'Generate exactly 16 weekly_plan rows. '
        'Schema: {'
        '"course_goal":"string",'
        '"teaching_methods":"string",'
        '"teaching_philosophy":"string",'
        '"learning_outcomes":[{"code":"LO1","courseLearningOutcome":"string","programLearningOutcome":"string","description":"string"}],'
        '"weekly_plan":[{"week":"1","topicModule":"string","courseOutcome":"string","questions":"string","tasks":"string","literature":"string","gradeStructure":"string"}],'
        '"rubric":[{"topicModule":"string","maxPercent":"100","maxWeight":"20","finalPoints":"20"}],'
        '"literature":{"required":["string"],"additional":["string"],"internetResources":["string"]}'
        '}\n\n'
        f'Course data: {json.dumps(course, ensure_ascii=False)}'
    )


def _parse_json_response(text):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    if not text.startswith('{'):
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
    if not text:
        raise RuntimeError('Gemini returned an empty AI-fill response.')
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as error:
        raise RuntimeError('Gemini returned invalid JSON for AI-fill.') from error
    if not isinstance(parsed, dict):
        raise RuntimeError('Gemini AI-fill response must be a JSON object.')
    return parsed


def _apply_ai_payload(syllabus, payload):
    policy, _ = CoursePolicy.objects.get_or_create(syllabus=syllabus)
    if _blank(syllabus.courseGoal):
        syllabus.courseGoal = _text(payload.get('course_goal'))
    if _blank(syllabus.teachingPhilosophy):
        syllabus.teachingPhilosophy = _text(payload.get('teaching_philosophy'))
    if _blank(policy.masteringDiscipline):
        policy.masteringDiscipline = _text(payload.get('teaching_methods'))
    syllabus.save(update_fields=['courseGoal', 'teachingPhilosophy', 'updatedAt'])
    policy.save(update_fields=['masteringDiscipline'])

    if _rows_empty(syllabus.learningOutcomes.all(), ['code', 'courseLearningOutcome', 'programLearningOutcome', 'description']):
        syllabus.learningOutcomes.all().delete()
        for index, row in enumerate(_list(payload.get('learning_outcomes')), start=1):
            LearningOutcomeRow.objects.create(
                syllabus=syllabus,
                order=index,
                code=_text(row.get('code')) or f'LO{index}',
                courseLearningOutcome=_text(row.get('courseLearningOutcome')),
                programLearningOutcome=_text(row.get('programLearningOutcome')),
                description=_text(row.get('description')),
            )

    if _rows_empty(syllabus.assessmentSystem.all(), ['topicModule', 'maxPercent', 'maxWeight', 'finalPoints']):
        syllabus.assessmentSystem.all().delete()
        for index, row in enumerate(_list(payload.get('rubric')), start=1):
            AssessmentRow.objects.create(
                syllabus=syllabus,
                order=index,
                topicModule=_text(row.get('topicModule')),
                maxPercent=_text(row.get('maxPercent')),
                maxWeight=_text(row.get('maxWeight')),
                finalPoints=_text(row.get('finalPoints')),
            )

    literature = payload.get('literature') if isinstance(payload.get('literature'), dict) else {}
    _apply_literature_if_empty(syllabus, LiteratureItem.TYPE_REQUIRED, literature.get('required'))
    _apply_literature_if_empty(syllabus, LiteratureItem.TYPE_ADDITIONAL, literature.get('additional'))
    _apply_literature_if_empty(syllabus, LiteratureItem.TYPE_INTERNET, literature.get('internetResources'))


def _ensure_minimum_weekly_plan(syllabus, weekly_plan_payload):
    existing = list(syllabus.thematicPlan.all())
    has_content = not _rows_empty(existing, ['week', 'topicModule', 'courseOutcome', 'questions', 'tasks'])
    if not has_content:
        syllabus.thematicPlan.all().delete()
        rows = _list(weekly_plan_payload)[:16]
        while len(rows) < 16:
            week = len(rows) + 1
            rows.append({
                'week': str(week),
                'topicModule': '',
                'courseOutcome': '',
                'questions': '',
                'tasks': '',
                'literature': '',
                'gradeStructure': '',
            })
        for index, row in enumerate(rows, start=1):
            ThematicPlanRow.objects.create(
                syllabus=syllabus,
                order=index,
                week=_text(row.get('week')) or str(index),
                topicModule=_text(row.get('topicModule')),
                courseOutcome=_text(row.get('courseOutcome')),
                questions=_text(row.get('questions')),
                tasks=_text(row.get('tasks')),
                literature=_text(row.get('literature')),
                gradeStructure=_text(row.get('gradeStructure')),
            )
        return

    while len(existing) < 16:
        week = len(existing) + 1
        existing.append(ThematicPlanRow.objects.create(syllabus=syllabus, order=week, week=str(week)))


def _apply_literature_if_empty(syllabus, item_type, values):
    current = LiteratureItem.objects.filter(syllabus=syllabus, type=item_type)
    if any(_text(item.text) for item in current):
        return
    current.delete()
    for index, value in enumerate([_text(item) for item in _list(values) if _text(item)], start=1):
        LiteratureItem.objects.create(syllabus=syllabus, type=item_type, order=index, text=value)


def _rows_empty(rows, fields):
    return not any(any(_text(getattr(row, field, '')) for field in fields) for row in rows)


def _blank(value):
    return not _text(value)


def _text(value):
    return str(value or '').strip()


def _list(value):
    return value if isinstance(value, list) else []
