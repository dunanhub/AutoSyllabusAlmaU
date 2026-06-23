# Generated manually for Syllabus Generator analytics.

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CeleryTaskLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('task_id', models.CharField(db_index=True, max_length=255)),
                ('task_type', models.CharField(choices=[('template_translation', 'Template translation'), ('syllabus_ai_fill', 'Syllabus AI fill'), ('render_translation', 'Rendered syllabus translation'), ('document_generation', 'Document generation')], max_length=64)),
                ('object_type', models.CharField(choices=[('template', 'Template'), ('syllabus', 'Syllabus')], max_length=32)),
                ('object_id', models.CharField(db_index=True, max_length=64)),
                ('object_title', models.CharField(blank=True, default='', max_length=255)),
                ('status', models.CharField(choices=[('queued', 'Queued'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='queued', max_length=24)),
                ('retry_action', models.CharField(choices=[('template_translate', 'Retry template translation'), ('syllabus_ai_fill', 'Retry syllabus AI fill'), ('syllabus_render_translate', 'Retry rendered translation'), ('syllabus_documents', 'Retry documents generation')], max_length=64)),
                ('error', models.TextField(blank=True, default='')),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='celery_task_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='celerytasklog',
            index=models.Index(fields=['owner', 'status'], name='analytics_c_owner_i_7e8173_idx'),
        ),
        migrations.AddIndex(
            model_name='celerytasklog',
            index=models.Index(fields=['owner', 'task_type'], name='analytics_c_owner_i_09cde0_idx'),
        ),
        migrations.AddIndex(
            model_name='celerytasklog',
            index=models.Index(fields=['owner', 'created_at'], name='analytics_c_owner_i_13e9a7_idx'),
        ),
    ]

