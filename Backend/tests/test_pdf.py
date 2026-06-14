from unittest.mock import patch

import pytest
from django.core.files.base import ContentFile
from rest_framework import status

from syllabuses.models import Syllabus
from syllabuses.services.pdf_service import generate_syllabus_pdf


pytestmark = pytest.mark.django_db


@patch('syllabuses.views.generate_syllabus_pdf_task.apply_async')
def test_generate_pdf_enqueues_background_task(apply_async, api_client, syllabus):
    response = api_client.post(f'/api/syllabuses/{syllabus.id}/generate-pdf/')

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data['status'] == Syllabus.PDF_STATUS_PROCESSING
    assert response.data['taskId']
    apply_async.assert_called_once()


@patch('syllabuses.views.generate_syllabus_pdf_task.apply_async')
def test_generate_pdf_does_not_enqueue_duplicate_task(apply_async, api_client, syllabus):
    syllabus.pdf_status = Syllabus.PDF_STATUS_PROCESSING
    syllabus.pdf_task_id = 'existing-task'
    syllabus.save(update_fields=['pdf_status', 'pdf_task_id'])

    response = api_client.post(f'/api/syllabuses/{syllabus.id}/generate-pdf/')

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {'taskId': 'existing-task', 'status': 'processing'}
    apply_async.assert_not_called()


def test_pdf_status_returns_processing_state(api_client, syllabus):
    syllabus.pdf_status = Syllabus.PDF_STATUS_PROCESSING
    syllabus.pdf_task_id = 'task-123'
    syllabus.save(update_fields=['pdf_status', 'pdf_task_id'])

    response = api_client.get(f'/api/syllabuses/{syllabus.id}/pdf-status/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['taskId'] == 'task-123'
    assert response.data['pdfStatus'] == Syllabus.PDF_STATUS_PROCESSING


def test_download_rejected_before_generation(api_client, syllabus):
    response = api_client.get(f'/api/syllabuses/{syllabus.id}/download-pdf/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_download_generated_pdf(api_client, syllabus, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    syllabus.pdf_file.save('syllabus_test.pdf', ContentFile(b'%PDF-1.7 test'), save=False)
    syllabus.pdf_status = Syllabus.PDF_STATUS_GENERATED
    syllabus.save(update_fields=['pdf_file', 'pdf_status'])

    response = api_client.get(f'/api/syllabuses/{syllabus.id}/download-pdf/')
    body = b''.join(response.streaming_content)

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/pdf'
    assert 'attachment;' in response['Content-Disposition']
    assert body.startswith(b'%PDF')


def test_pdf_service_generates_real_pdf(syllabus, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path

    generated = generate_syllabus_pdf(syllabus)

    assert generated.pdf_status == Syllabus.PDF_STATUS_GENERATED
    assert generated.pdf_generated_at is not None
    with generated.pdf_file.open('rb') as pdf:
        assert pdf.read(4) == b'%PDF'


@patch('syllabuses.services.pdf_service.HTML.write_pdf', side_effect=RuntimeError('Render failed'))
def test_pdf_service_records_failure_and_keeps_previous_file(
    write_pdf,
    syllabus,
    tmp_path,
    settings,
):
    settings.MEDIA_ROOT = tmp_path
    syllabus.pdf_file.save('existing.pdf', ContentFile(b'%PDF old'), save=False)
    syllabus.pdf_status = Syllabus.PDF_STATUS_GENERATED
    syllabus.save(update_fields=['pdf_file', 'pdf_status'])
    old_name = syllabus.pdf_file.name

    with pytest.raises(RuntimeError, match='Render failed'):
        generate_syllabus_pdf(syllabus)

    syllabus.refresh_from_db()
    assert syllabus.pdf_status == Syllabus.PDF_STATUS_FAILED
    assert syllabus.pdf_error == 'Render failed'
    assert syllabus.pdf_file.name == old_name
    assert syllabus.pdf_file.storage.exists(old_name)
    write_pdf.assert_called_once()
