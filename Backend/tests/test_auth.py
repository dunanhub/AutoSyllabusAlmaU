import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient


pytestmark = pytest.mark.django_db


def test_login_returns_access_and_refresh_tokens(user):
    response = APIClient().post('/api/auth/login/', {
        'email': user.email,
        'password': 'StrongPassword123',
    }, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['access']
    assert response.data['refresh']


def test_login_rejects_invalid_password(user):
    response = APIClient().post('/api/auth/login/', {
        'email': user.email,
        'password': 'wrong-password',
    }, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_returns_new_access_token(user):
    client = APIClient()
    login = client.post('/api/auth/login/', {
        'email': user.email,
        'password': 'StrongPassword123',
    }, format='json')
    response = client.post('/api/auth/refresh/', {
        'refresh': login.data['refresh'],
    }, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['access']


def test_me_returns_authenticated_user(api_client, user):
    response = api_client.get('/api/auth/me/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user.email


def test_syllabus_list_requires_authentication():
    response = APIClient().get('/api/syllabuses/')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def registration_payload(**overrides):
    payload = {
        'firstName': 'New',
        'lastName': 'Teacher',
        'email': 'new.teacher@example.com',
        'password': 'StrongRegistration123!',
        'passwordConfirm': 'StrongRegistration123!',
    }
    payload.update(overrides)
    return payload


def test_register_returns_user_and_tokens():
    response = APIClient().post('/api/auth/register/', registration_payload(), format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['user']['email'] == 'new.teacher@example.com'
    assert response.data['user']['first_name'] == 'New'
    assert response.data['access']
    assert response.data['refresh']


def test_register_hashes_password():
    APIClient().post('/api/auth/register/', registration_payload(), format='json')

    created_user = get_user_model().objects.get(email='new.teacher@example.com')
    assert created_user.password != 'StrongRegistration123!'
    assert created_user.check_password('StrongRegistration123!')


def test_register_rejects_duplicate_email_case_insensitively(user):
    response = APIClient().post(
        '/api/auth/register/',
        registration_payload(email=user.email.upper()),
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


def test_register_rejects_mismatched_passwords():
    response = APIClient().post(
        '/api/auth/register/',
        registration_payload(passwordConfirm='DifferentPassword123!'),
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'passwordConfirm' in response.data


def test_register_rejects_weak_password():
    response = APIClient().post(
        '/api/auth/register/',
        registration_payload(password='12345678', passwordConfirm='12345678'),
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data


def test_register_access_token_opens_me_endpoint():
    client = APIClient()
    register = client.post('/api/auth/register/', registration_payload(), format='json')
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {register.data['access']}")

    response = client.get('/api/auth/me/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'new.teacher@example.com'
