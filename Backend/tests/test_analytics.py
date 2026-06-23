import pytest
from rest_framework import status

from analytics.models import CeleryTaskLog
from syllabuses.models import Syllabus
from template_builder.models import SyllabusTemplate


pytestmark = pytest.mark.django_db


def test_analytics_summary_returns_owner_kpis(api_client, user, syllabus):
    template = SyllabusTemplate.objects.create(
        owner=user,
        title='Main template',
        description='Ready template',
        content='<p>{{course.code_and_name}}</p>',
        validation_status=SyllabusTemplate.VALIDATION_VALID,
        is_default=True,
        translation_status=SyllabusTemplate.TRANSLATION_COMPLETED,
    )
    CeleryTaskLog.objects.create(
        owner=user,
        task_id='task-1',
        task_type=CeleryTaskLog.TYPE_TEMPLATE_TRANSLATION,
        object_type=CeleryTaskLog.OBJECT_TEMPLATE,
        object_id=str(template.id),
        object_title=template.title,
        status=CeleryTaskLog.STATUS_COMPLETED,
        retry_action=CeleryTaskLog.ACTION_TEMPLATE_TRANSLATE,
    )

    response = api_client.get('/api/analytics/summary/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['syllabuses']['total'] == 1
    assert response.data['templates']['total'] == 1
    assert response.data['templates']['default'] == 1
    assert response.data['automation']['tasks'][CeleryTaskLog.STATUS_COMPLETED] == 1


def test_analytics_tasks_are_limited_to_current_owner(api_client, user, other_user, syllabus):
    own_log = CeleryTaskLog.objects.create(
        owner=user,
        task_id='own-task',
        task_type=CeleryTaskLog.TYPE_SYLLABUS_AI_FILL,
        object_type=CeleryTaskLog.OBJECT_SYLLABUS,
        object_id=str(syllabus.id),
        object_title='Own syllabus',
        status=CeleryTaskLog.STATUS_FAILED,
        retry_action=CeleryTaskLog.ACTION_SYLLABUS_AI_FILL,
        error='Gemini 503',
    )
    CeleryTaskLog.objects.create(
        owner=other_user,
        task_id='other-task',
        task_type=CeleryTaskLog.TYPE_SYLLABUS_AI_FILL,
        object_type=CeleryTaskLog.OBJECT_SYLLABUS,
        object_id='other-object',
        object_title='Other syllabus',
        status=CeleryTaskLog.STATUS_FAILED,
        retry_action=CeleryTaskLog.ACTION_SYLLABUS_AI_FILL,
    )

    response = api_client.get('/api/analytics/tasks/?status=failed&search=Gemini')

    assert response.status_code == status.HTTP_200_OK
    assert [item['id'] for item in response.data] == [str(own_log.id)]


def test_retry_rejects_completed_task(api_client, user, syllabus):
    log = CeleryTaskLog.objects.create(
        owner=user,
        task_id='completed-task',
        task_type=CeleryTaskLog.TYPE_DOCUMENT_GENERATION,
        object_type=CeleryTaskLog.OBJECT_SYLLABUS,
        object_id=str(syllabus.id),
        object_title='Completed syllabus',
        status=CeleryTaskLog.STATUS_COMPLETED,
        retry_action=CeleryTaskLog.ACTION_SYLLABUS_DOCUMENTS,
    )

    response = api_client.post(f'/api/analytics/tasks/{log.id}/retry/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'Only failed tasks can be retried.'


def test_retry_failed_document_task_starts_new_task(api_client, user, syllabus, monkeypatch):
    called = {}

    def fake_apply_async(args=None, task_id=None, **kwargs):
        called['args'] = args
        called['task_id'] = task_id

    monkeypatch.setattr('analytics.views.generate_syllabus_pdf_task.apply_async', fake_apply_async)
    log = CeleryTaskLog.objects.create(
        owner=user,
        task_id='failed-task',
        task_type=CeleryTaskLog.TYPE_DOCUMENT_GENERATION,
        object_type=CeleryTaskLog.OBJECT_SYLLABUS,
        object_id=str(syllabus.id),
        object_title='Failed syllabus',
        status=CeleryTaskLog.STATUS_FAILED,
        retry_action=CeleryTaskLog.ACTION_SYLLABUS_DOCUMENTS,
        error='PDF failed',
    )

    response = api_client.post(f'/api/analytics/tasks/{log.id}/retry/')

    syllabus.refresh_from_db()
    assert response.status_code == status.HTTP_202_ACCEPTED, response.data
    assert response.data['status'] == CeleryTaskLog.STATUS_PROCESSING
    assert response.data['taskId'] == called['task_id']
    assert called['args'] == [str(syllabus.id)]
    assert syllabus.pdf_status == Syllabus.PDF_STATUS_PROCESSING
