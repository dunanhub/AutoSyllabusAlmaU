from unittest.mock import patch

import pytest
from rest_framework import status

from template_builder.models import SyllabusTemplate
from template_builder.services.translation_service import TemplateTranslationService


pytestmark = pytest.mark.django_db


def template_payload(**overrides):
    payload = {
        'title': 'Main syllabus template',
        'description': 'Template for AlmaU syllabus',
        'content': '<h1>{{course.code_and_name}}</h1><p>Описание курса</p>',
        'markers': [
            {
                'id': 'marker-1',
                'key': 'course.code_and_name',
                'label': 'Код и название дисциплины',
                'token': '{{course.code_and_name}}',
                'type': 'text',
                'group': 'Курс',
                'description': '',
            }
        ],
        'validationStatus': 'valid',
        'sourceLanguage': 'ru',
    }
    payload.update(overrides)
    return payload


def test_template_create_lists_owner_templates(api_client, settings):
    settings.GEMINI_API_KEY = ''
    response = api_client.post('/api/templates/', template_payload(validationStatus='invalid'), format='json')

    assert response.status_code == status.HTTP_201_CREATED
    listing = api_client.get('/api/templates/')
    assert listing.status_code == status.HTTP_200_OK
    assert listing.data[0]['title'] == 'Main syllabus template'


def test_template_list_is_owner_scoped(api_client, other_user):
    SyllabusTemplate.objects.create(
        owner=other_user,
        title='Hidden',
        description='Other user template',
        content='<p>Hidden</p>',
    )

    response = api_client.get('/api/templates/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


def test_draft_template_cannot_be_default(api_client):
    create = api_client.post('/api/templates/', template_payload(validationStatus='invalid'), format='json')

    response = api_client.post(f"/api/templates/{create.data['id']}/set-default/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_valid_template_can_be_default(api_client):
    with patch('template_builder.views.translate_template_task.apply_async'):
        create = api_client.post('/api/templates/', template_payload(validationStatus='valid'), format='json')

    response = api_client.post(f"/api/templates/{create.data['id']}/set-default/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data['isDefault'] is True


def test_translate_endpoint_returns_existing_processing_task(api_client):
    with patch('template_builder.views.translate_template_task.apply_async'):
        create = api_client.post('/api/templates/', template_payload(validationStatus='valid'), format='json')

        response = api_client.post(f"/api/templates/{create.data['id']}/translate/")

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data['status'] == SyllabusTemplate.TRANSLATION_TRANSLATING
    assert response.data['taskId']


def test_translations_endpoint_returns_language_content(api_client, user):
    template = SyllabusTemplate.objects.create(
        owner=user,
        title='Translated',
        description='Translated template',
        content='<p>Source</p>',
        validation_status=SyllabusTemplate.VALIDATION_VALID,
        content_kz='<p>KZ</p>',
        content_ru='<p>RU</p>',
        content_en='<p>EN</p>',
        translation_status=SyllabusTemplate.TRANSLATION_COMPLETED,
    )

    response = api_client.get(f'/api/templates/{template.id}/translations/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['contentKz'] == '<p>KZ</p>'
    assert response.data['translationStatus'] == SyllabusTemplate.TRANSLATION_COMPLETED


def test_translation_service_preserves_markers(settings):
    settings.GEMINI_API_KEY = 'test-key'
    template = SyllabusTemplate(
        title='Template',
        description='Description',
        content='<h1>{{course.code_and_name}}</h1><p>Описание</p>',
        source_language=SyllabusTemplate.LANGUAGE_RU,
    )

    with patch.object(TemplateTranslationService, '_translate_html', return_value='<h1>__SGS_MARKER_0__</h1><p>Translated</p>'):
        translated = TemplateTranslationService().translate_template(template)

    assert '{{course.code_and_name}}' in translated[SyllabusTemplate.LANGUAGE_KZ]
    assert translated[SyllabusTemplate.LANGUAGE_RU] == template.content


def test_translation_service_rejects_marker_mutation(settings):
    settings.GEMINI_API_KEY = 'test-key'
    template = SyllabusTemplate(
        title='Template',
        description='Description',
        content='<p>{{course.code_and_name}}</p>',
        source_language=SyllabusTemplate.LANGUAGE_RU,
    )

    with patch.object(TemplateTranslationService, '_translate_html', return_value='<p>Broken</p>'):
        with pytest.raises(ValueError):
            TemplateTranslationService().translate_template(template)
