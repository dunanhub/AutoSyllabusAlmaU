from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SyllabusViewSet

router = DefaultRouter()
router.register(r'syllabuses', SyllabusViewSet, basename='syllabus')

urlpatterns = [
    path('', include(router.urls)),
]
