from django.utils import timezone

from .models import CeleryTaskLog


def create_task_log(*, owner, task_id, task_type, object_type, object_id, object_title, retry_action):
    return CeleryTaskLog.objects.create(
        owner=owner,
        task_id=task_id,
        task_type=task_type,
        object_type=object_type,
        object_id=str(object_id),
        object_title=object_title or '',
        status=CeleryTaskLog.STATUS_PROCESSING,
        retry_action=retry_action,
        started_at=timezone.now(),
    )


def mark_task_completed(task_id):
    CeleryTaskLog.objects.filter(task_id=task_id).update(
        status=CeleryTaskLog.STATUS_COMPLETED,
        error='',
        finished_at=timezone.now(),
        updated_at=timezone.now(),
    )


def mark_task_failed(task_id, error):
    CeleryTaskLog.objects.filter(task_id=task_id).update(
        status=CeleryTaskLog.STATUS_FAILED,
        error=str(error),
        finished_at=timezone.now(),
        updated_at=timezone.now(),
    )


def syllabus_title(syllabus):
    title_info = getattr(syllabus, 'titleInfo', None)
    if title_info and title_info.codeAndName:
        return title_info.codeAndName
    return str(syllabus.id)

