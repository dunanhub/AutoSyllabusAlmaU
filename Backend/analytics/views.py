import uuid
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from syllabuses.models import Syllabus
from syllabuses.tasks import ai_fill_syllabus_task, generate_syllabus_pdf_task, translate_rendered_syllabus_task
from template_builder.models import SyllabusTemplate
from template_builder.tasks import translate_template_task

from .models import CeleryTaskLog
from .serializers import CeleryTaskLogSerializer
from .services import create_task_log, syllabus_title


def user_syllabuses(user):
    queryset = Syllabus.objects.select_related('titleInfo', 'owner')
    return queryset if user.is_staff else queryset.filter(owner=user)


def user_templates(user):
    queryset = SyllabusTemplate.objects.select_related('owner')
    return queryset if user.is_staff else queryset.filter(owner=user)


def user_tasks(user):
    queryset = CeleryTaskLog.objects.select_related('owner')
    return queryset if user.is_staff else queryset.filter(owner=user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary(request):
    syllabuses = user_syllabuses(request.user)
    templates = user_templates(request.user)
    tasks = user_tasks(request.user)

    syllabus_statuses = dict(syllabuses.values_list('status').annotate(count=Count('id')))
    pdf_statuses = dict(syllabuses.values_list('pdf_status').annotate(count=Count('id')))
    ai_statuses = dict(syllabuses.values_list('ai_fill_status').annotate(count=Count('id')))
    render_statuses = dict(syllabuses.values_list('render_translation_status').annotate(count=Count('id')))
    template_validation = dict(templates.values_list('validation_status').annotate(count=Count('id')))
    template_translation = dict(templates.values_list('translation_status').annotate(count=Count('id')))
    task_statuses = dict(tasks.values_list('status').annotate(count=Count('id')))

    recent_errors = CeleryTaskLogSerializer(
        tasks.filter(status=CeleryTaskLog.STATUS_FAILED)[:5],
        many=True,
    ).data
    active_tasks = CeleryTaskLogSerializer(
        tasks.filter(status__in=[CeleryTaskLog.STATUS_QUEUED, CeleryTaskLog.STATUS_PROCESSING])[:5],
        many=True,
    ).data

    return Response({
        'syllabuses': {
            'total': syllabuses.count(),
            'draft': syllabus_statuses.get(Syllabus.STATUS_DRAFT, 0),
            'ready': syllabus_statuses.get(Syllabus.STATUS_READY, 0),
        },
        'templates': {
            'total': templates.count(),
            'valid': template_validation.get(SyllabusTemplate.VALIDATION_VALID, 0),
            'draft': template_validation.get(SyllabusTemplate.VALIDATION_INVALID, 0),
            'default': templates.filter(is_default=True).count(),
            'translation': template_translation,
        },
        'documents': {
            'generated': pdf_statuses.get(Syllabus.PDF_STATUS_GENERATED, 0),
            'processing': pdf_statuses.get(Syllabus.PDF_STATUS_PROCESSING, 0),
            'failed': pdf_statuses.get(Syllabus.PDF_STATUS_FAILED, 0),
            'notGenerated': pdf_statuses.get(Syllabus.PDF_STATUS_NOT_GENERATED, 0),
        },
        'automation': {
            'ai': ai_statuses,
            'renderTranslation': render_statuses,
            'tasks': task_statuses,
            'failedTotal': tasks.filter(status=CeleryTaskLog.STATUS_FAILED).count(),
            'processingTotal': tasks.filter(status__in=[CeleryTaskLog.STATUS_QUEUED, CeleryTaskLog.STATUS_PROCESSING]).count(),
        },
        'recentErrors': recent_errors,
        'activeTasks': active_tasks,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks(request):
    queryset = user_tasks(request.user)
    task_status = request.query_params.get('status')
    task_type = request.query_params.get('type')
    search = (request.query_params.get('search') or '').strip()
    period = request.query_params.get('period', 'all')

    if task_status:
        queryset = queryset.filter(status=task_status)
    if task_type:
        queryset = queryset.filter(task_type=task_type)
    if search:
        queryset = queryset.filter(
            Q(object_title__icontains=search)
            | Q(task_id__icontains=search)
            | Q(error__icontains=search)
        )
    if period in {'today', '7d', '30d'}:
        now = timezone.now()
        if period == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == '7d':
            start = now - timedelta(days=7)
        else:
            start = now - timedelta(days=30)
        queryset = queryset.filter(created_at__gte=start)

    return Response(CeleryTaskLogSerializer(queryset[:200], many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retry_task(request, task_id):
    original = user_tasks(request.user).filter(id=task_id).first()
    if not original:
        return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
    if original.status != CeleryTaskLog.STATUS_FAILED:
        return Response({'detail': 'Only failed tasks can be retried.'}, status=status.HTTP_400_BAD_REQUEST)

    new_task_id = str(uuid.uuid4())
    try:
        if original.retry_action == CeleryTaskLog.ACTION_TEMPLATE_TRANSLATE:
            template = user_templates(request.user).get(id=original.object_id)
            template.translation_status = SyllabusTemplate.TRANSLATION_TRANSLATING
            template.translation_error = ''
            template.translated_at = None
            template.translation_task_id = new_task_id
            template.save(update_fields=['translation_status', 'translation_error', 'translated_at', 'translation_task_id', 'updated_at'])
            log = create_task_log(
                owner=template.owner,
                task_id=new_task_id,
                task_type=CeleryTaskLog.TYPE_TEMPLATE_TRANSLATION,
                object_type=CeleryTaskLog.OBJECT_TEMPLATE,
                object_id=template.id,
                object_title=template.title,
                retry_action=CeleryTaskLog.ACTION_TEMPLATE_TRANSLATE,
            )
            translate_template_task.apply_async(args=[str(template.id)], task_id=new_task_id)
        else:
            syllabus = user_syllabuses(request.user).get(id=original.object_id)
            if original.retry_action == CeleryTaskLog.ACTION_SYLLABUS_AI_FILL:
                syllabus.ai_fill_status = Syllabus.AI_FILL_PROCESSING
                syllabus.ai_fill_error = ''
                syllabus.ai_fill_task_id = new_task_id
                syllabus.ai_filled_at = None
                syllabus.save(update_fields=['ai_fill_status', 'ai_fill_error', 'ai_fill_task_id', 'ai_filled_at', 'updatedAt'])
                task_type = CeleryTaskLog.TYPE_SYLLABUS_AI_FILL
                retry_action = CeleryTaskLog.ACTION_SYLLABUS_AI_FILL
                task = ai_fill_syllabus_task
            elif original.retry_action == CeleryTaskLog.ACTION_SYLLABUS_RENDER_TRANSLATE:
                syllabus.render_translation_status = Syllabus.RENDER_TRANSLATION_TRANSLATING
                syllabus.render_translation_error = ''
                syllabus.render_translation_task_id = new_task_id
                syllabus.render_translated_at = None
                syllabus.save(update_fields=['render_translation_status', 'render_translation_error', 'render_translation_task_id', 'render_translated_at', 'updatedAt'])
                task_type = CeleryTaskLog.TYPE_RENDER_TRANSLATION
                retry_action = CeleryTaskLog.ACTION_SYLLABUS_RENDER_TRANSLATE
                task = translate_rendered_syllabus_task
            elif original.retry_action == CeleryTaskLog.ACTION_SYLLABUS_DOCUMENTS:
                syllabus.pdf_status = Syllabus.PDF_STATUS_PROCESSING
                syllabus.pdf_error = ''
                syllabus.pdf_task_id = new_task_id
                syllabus.pdf_generated_at = None
                syllabus.save(update_fields=['pdf_status', 'pdf_error', 'pdf_task_id', 'pdf_generated_at'])
                task_type = CeleryTaskLog.TYPE_DOCUMENT_GENERATION
                retry_action = CeleryTaskLog.ACTION_SYLLABUS_DOCUMENTS
                task = generate_syllabus_pdf_task
            else:
                return Response({'detail': 'Unsupported retry action.'}, status=status.HTTP_400_BAD_REQUEST)

            log = create_task_log(
                owner=syllabus.owner,
                task_id=new_task_id,
                task_type=task_type,
                object_type=CeleryTaskLog.OBJECT_SYLLABUS,
                object_id=syllabus.id,
                object_title=syllabus_title(syllabus),
                retry_action=retry_action,
            )
            task.apply_async(args=[str(syllabus.id)], task_id=new_task_id)
    except Exception as error:
        return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(CeleryTaskLogSerializer(log).data, status=status.HTTP_202_ACCEPTED)
