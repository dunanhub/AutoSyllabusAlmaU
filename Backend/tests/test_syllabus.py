import pytest
from rest_framework import status

from syllabuses.models import AssessmentRow, CoursePolicy, LearningOutcomeRow, LiteratureItem, Syllabus, SyllabusTitleInfo, ThematicPlanRow
from syllabuses.tasks import _is_temporary_gemini_error


pytestmark = pytest.mark.django_db


def test_list_only_returns_current_users_syllabuses(api_client, syllabus, other_user):
    other = Syllabus.objects.create(owner=other_user)
    SyllabusTitleInfo.objects.create(syllabus=other, codeAndName='OTHER')

    response = api_client.get('/api/syllabuses/')

    assert response.status_code == status.HTTP_200_OK
    assert [item['id'] for item in response.data] == [str(syllabus.id)]


def test_create_syllabus(api_client, syllabus_payload, user):
    response = api_client.post('/api/syllabuses/', syllabus_payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED, response.data
    created = Syllabus.objects.get(id=response.data['id'])
    assert created.owner == user
    assert created.titleInfo.codeAndName == 'NEW 1001 — New course'
    assert created.titleInfo.qrUrl == 'https://almau.edu.kz/syllabus/new-1001'
    assert created.titleInfo.schoolId == 'digital-economics'
    assert response.data['titleInfo']['schoolName'] == 'School of Digital Technologies and Economics'
    assert response.data['titleInfo']['qrUrl'] == 'https://almau.edu.kz/syllabus/new-1001'


def test_update_syllabus_invalidates_generated_pdf(api_client, syllabus, syllabus_payload):
    syllabus.pdf_status = Syllabus.PDF_STATUS_GENERATED
    syllabus.save(update_fields=['pdf_status'])
    payload = {**syllabus_payload, 'courseDescription': 'Updated description'}

    response = api_client.put(f'/api/syllabuses/{syllabus.id}/', payload, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['courseDescription'] == 'Updated description'
    assert response.data['pdfStatus'] == Syllabus.PDF_STATUS_NOT_GENERATED


def test_delete_syllabus(api_client, syllabus):
    response = api_client.delete(f'/api/syllabuses/{syllabus.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Syllabus.objects.filter(id=syllabus.id).exists()


def test_duplicate_syllabus(api_client, syllabus):
    response = api_client.post(f'/api/syllabuses/{syllabus.id}/duplicate/')

    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data['id'] != str(syllabus.id)
    assert response.data['status'] == Syllabus.STATUS_DRAFT
    assert Syllabus.objects.count() == 2


def test_set_status_does_not_invalidate_pdf(api_client, syllabus):
    syllabus.pdf_status = Syllabus.PDF_STATUS_GENERATED
    syllabus.save(update_fields=['pdf_status'])

    response = api_client.post(
        f'/api/syllabuses/{syllabus.id}/set-status/',
        {'status': 'ready'},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == Syllabus.STATUS_READY
    assert response.data['pdfStatus'] == Syllabus.PDF_STATUS_GENERATED


def test_list_cache_is_invalidated_after_mutation(api_client, syllabus):
    first = api_client.get('/api/syllabuses/')
    syllabus.titleInfo.codeAndName = 'CHANGED DIRECTLY'
    syllabus.titleInfo.save(update_fields=['codeAndName'])
    cached = api_client.get('/api/syllabuses/')
    assert cached.data[0]['titleInfo']['codeAndName'] == first.data[0]['titleInfo']['codeAndName']

    api_client.post(
        f'/api/syllabuses/{syllabus.id}/set-status/',
        {'status': 'ready'},
        format='json',
    )
    refreshed = api_client.get('/api/syllabuses/')
    assert refreshed.data[0]['titleInfo']['codeAndName'] == 'CHANGED DIRECTLY'


def test_detail_cache_is_invalidated_after_update(api_client, syllabus):
    url = f'/api/syllabuses/{syllabus.id}/'
    first = api_client.get(url)
    syllabus.courseDescription = 'CHANGED DIRECTLY'
    syllabus.save(update_fields=['courseDescription'])
    cached = api_client.get(url)
    assert cached.data['courseDescription'] == first.data['courseDescription']

    response = api_client.patch(url, {'courseGoal': 'Mutation'}, format='json')
    assert response.status_code == status.HTTP_200_OK
    refreshed = api_client.get(url)
    assert refreshed.data['courseDescription'] == 'CHANGED DIRECTLY'


def test_ai_fill_returns_completed_when_no_empty_blocks(api_client, syllabus):
    _fill_ai_sections(syllabus)

    response = api_client.post(f'/api/syllabuses/{syllabus.id}/ai-fill/')

    syllabus.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == Syllabus.AI_FILL_COMPLETED
    assert response.data['taskId'] == ''
    assert syllabus.ai_fill_status == Syllabus.AI_FILL_COMPLETED


def test_ai_fill_does_not_enqueue_duplicate_when_processing(api_client, syllabus):
    syllabus.ai_fill_status = Syllabus.AI_FILL_PROCESSING
    syllabus.ai_fill_task_id = 'existing-task-id'
    syllabus.save(update_fields=['ai_fill_status', 'ai_fill_task_id'])

    response = api_client.post(f'/api/syllabuses/{syllabus.id}/ai-fill/')

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {'taskId': 'existing-task-id', 'status': Syllabus.AI_FILL_PROCESSING}


def test_gemini_high_demand_error_is_retryable():
    error = RuntimeError("503 UNAVAILABLE. This model is currently experiencing high demand.")

    assert _is_temporary_gemini_error(error)


def _fill_ai_sections(syllabus):
    syllabus.courseGoal = 'Filled goal'
    syllabus.teachingPhilosophy = 'Filled philosophy'
    syllabus.save(update_fields=['courseGoal', 'teachingPhilosophy'])
    CoursePolicy.objects.create(syllabus=syllabus, masteringDiscipline='Filled teaching methods')
    LearningOutcomeRow.objects.create(
        syllabus=syllabus,
        order=1,
        code='LO1',
        courseLearningOutcome='Outcome',
        programLearningOutcome='Program outcome',
        description='Description',
    )
    for week in range(1, 17):
        ThematicPlanRow.objects.create(
            syllabus=syllabus,
            order=week,
            week=str(week),
            topicModule=f'Topic {week}',
            courseOutcome='Outcome',
            questions='Questions',
            tasks='Tasks',
            literature='Literature',
            gradeStructure='Grade',
        )
    AssessmentRow.objects.create(
        syllabus=syllabus,
        order=1,
        topicModule='Current work',
        maxPercent='100',
        maxWeight='20',
        finalPoints='20',
    )
    LiteratureItem.objects.create(syllabus=syllabus, type=LiteratureItem.TYPE_REQUIRED, order=1, text='Required')
    LiteratureItem.objects.create(syllabus=syllabus, type=LiteratureItem.TYPE_ADDITIONAL, order=1, text='Additional')
    LiteratureItem.objects.create(syllabus=syllabus, type=LiteratureItem.TYPE_INTERNET, order=1, text='Internet')
