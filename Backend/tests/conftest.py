import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient

from syllabuses.models import Syllabus, SyllabusTitleInfo


@pytest.fixture(autouse=True)
def clean_cache(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        email='teacher@example.com',
        password='StrongPassword123',
        first_name='Test',
        last_name='Teacher',
    )


@pytest.fixture
def other_user(db):
    return get_user_model().objects.create_user(
        email='other@example.com',
        password='StrongPassword123',
    )


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def syllabus(user):
    item = Syllabus.objects.create(
        owner=user,
        status=Syllabus.STATUS_DRAFT,
        completion=40,
        courseDescription='Initial description',
        courseGoal='Initial goal',
    )
    SyllabusTitleInfo.objects.create(
        syllabus=item,
        codeAndName='TEST 1001 — Test course',
        languageOfEducation='EN',
        instructorName='Test Teacher',
    )
    return item


@pytest.fixture
def syllabus_payload():
    return {
        'status': 'draft',
        'completion': 25,
        'courseDescription': 'Created through API',
        'courseGoal': 'Test API creation',
        'teachingPhilosophy': '',
        'titleInfo': {
            'codeAndName': 'NEW 1001 — New course',
            'credits': '5',
            'totalHours': '150',
            'classroomHours': '45',
            'independentWorkHours': '105',
            'prerequisites': '',
            'levelOfTraining': 'Bachelor',
            'semester': '1',
            'educationalProgram': 'Testing',
            'languageOfEducation': 'EN',
            'proficiencyLevel': '',
            'formatOfTraining': 'Full-time',
            'instructorName': 'Test Teacher',
            'instructorDegree': '',
            'instructorEmail': 'teacher@example.com',
            'instructorContacts': '',
            'timeAndPlace': '',
        },
        'classSchedule': [],
        'learningOutcomes': [],
        'thematicPlan': [],
        'assessmentSystem': [],
        'literature': {
            'required': [],
            'additional': [],
            'internetResources': [],
        },
        'coursePolicy': {
            'masteringDiscipline': '',
            'allowed': '',
            'notAllowed': '',
            'examEthics': '',
            'informationCommunication': '',
        },
        'signatures': {
            'preparedByName': '',
            'preparedByPosition': '',
            'preparedByDate': '',
            'signatureImage': '',
            'stampImage': '',
        },
    }
