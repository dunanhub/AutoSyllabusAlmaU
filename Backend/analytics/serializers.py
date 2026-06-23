from rest_framework import serializers

from .models import CeleryTaskLog


class CeleryTaskLogSerializer(serializers.ModelSerializer):
    taskId = serializers.CharField(source='task_id', read_only=True)
    startedAt = serializers.DateTimeField(source='started_at', read_only=True, allow_null=True)
    finishedAt = serializers.DateTimeField(source='finished_at', read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    taskType = serializers.CharField(source='task_type', read_only=True)
    objectType = serializers.CharField(source='object_type', read_only=True)
    objectId = serializers.CharField(source='object_id', read_only=True)
    objectTitle = serializers.CharField(source='object_title', read_only=True)
    retryAction = serializers.CharField(source='retry_action', read_only=True)

    class Meta:
        model = CeleryTaskLog
        fields = [
            'id', 'taskId', 'taskType', 'objectType', 'objectId', 'objectTitle',
            'status', 'retryAction', 'error', 'startedAt', 'finishedAt', 'createdAt', 'updatedAt',
        ]
