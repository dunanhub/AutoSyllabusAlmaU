import pytest
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
