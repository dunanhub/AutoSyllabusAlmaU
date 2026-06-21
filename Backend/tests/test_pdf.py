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


def test_download_generated_document_variants(api_client, syllabus, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    syllabus.pdf_file_ru.save('syllabus_ru.pdf', ContentFile(b'%PDF ru'), save=False)
    syllabus.docx_file_en.save('syllabus_en.docx', ContentFile(b'PK docx'), save=False)
    syllabus.pdf_status = Syllabus.PDF_STATUS_GENERATED
    syllabus.save(update_fields=['pdf_file_ru', 'docx_file_en', 'pdf_status'])

    pdf_response = api_client.get(f'/api/syllabuses/{syllabus.id}/download-document/?language=ru&format=pdf')
    docx_response = api_client.get(f'/api/syllabuses/{syllabus.id}/download-document/?language=en&format=docx')

    assert pdf_response.status_code == status.HTTP_200_OK
    assert pdf_response['Content-Type'] == 'application/pdf'
    assert b''.join(pdf_response.streaming_content).startswith(b'%PDF')
    assert docx_response.status_code == status.HTTP_200_OK
    assert docx_response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert b''.join(docx_response.streaming_content).startswith(b'PK')


def test_pdf_service_generates_real_pdf(syllabus, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    syllabus.rendered_content_ru = '<p>Русская версия</p>'
    syllabus.rendered_content_kz = '<p>Қазақша нұсқа</p>'
    syllabus.rendered_content_en = '<p>English version</p>'
    syllabus.save(update_fields=['rendered_content_ru', 'rendered_content_kz', 'rendered_content_en'])

    generated = generate_syllabus_pdf(syllabus)

    assert generated.pdf_status == Syllabus.PDF_STATUS_GENERATED
    assert generated.pdf_generated_at is not None
    for field in ['pdf_file_ru', 'pdf_file_kz', 'pdf_file_en']:
        with getattr(generated, field).open('rb') as pdf:
            assert pdf.read(4) == b'%PDF'
    for field in ['docx_file_ru', 'docx_file_kz', 'docx_file_en']:
        with getattr(generated, field).open('rb') as docx:
            assert docx.read(2) == b'PK'


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
    syllabus.rendered_content_ru = '<p>Русская версия</p>'
    syllabus.rendered_content_kz = '<p>Қазақша нұсқа</p>'
    syllabus.rendered_content_en = '<p>English version</p>'
    syllabus.save(update_fields=[
        'pdf_file', 'pdf_status', 'rendered_content_ru', 'rendered_content_kz', 'rendered_content_en'
    ])
    old_name = syllabus.pdf_file.name

    with pytest.raises(RuntimeError, match='Render failed'):
        generate_syllabus_pdf(syllabus)

    syllabus.refresh_from_db()
    assert syllabus.pdf_status == Syllabus.PDF_STATUS_FAILED
    assert syllabus.pdf_error == 'Render failed'
    assert syllabus.pdf_file.name == old_name
    assert syllabus.pdf_file.storage.exists(old_name)
    write_pdf.assert_called_once()
