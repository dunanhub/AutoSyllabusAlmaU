from django.urls import path

from . import views


urlpatterns = [
    path('analytics/summary/', views.summary),
    path('analytics/tasks/', views.tasks),
    path('analytics/tasks/<uuid:task_id>/retry/', views.retry_task),
]

