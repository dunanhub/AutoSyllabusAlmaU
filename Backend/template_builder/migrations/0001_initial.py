# Generated for Syllabus Generator System template builder.

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
            name='SyllabusTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('content', models.TextField(blank=True, default='')),
                ('markers', models.JSONField(blank=True, default=list)),
                ('validation_status', models.CharField(choices=[('valid', 'Valid'), ('invalid', 'Invalid')], default='invalid', max_length=16)),
                ('is_default', models.BooleanField(default=False)),
                ('source_language', models.CharField(choices=[('kz', 'Kazakh'), ('ru', 'Russian'), ('en', 'English')], default='ru', max_length=8)),
                ('content_kz', models.TextField(blank=True, default='')),
                ('content_ru', models.TextField(blank=True, default='')),
                ('content_en', models.TextField(blank=True, default='')),
                ('translation_status', models.CharField(choices=[('not_translated', 'Not translated'), ('translating', 'Translating'), ('completed', 'Completed'), ('failed', 'Failed')], default='not_translated', max_length=24)),
                ('translation_error', models.TextField(blank=True, default='')),
                ('translated_at', models.DateTimeField(blank=True, null=True)),
                ('translation_task_id', models.CharField(blank=True, default='', max_length=255)),
                ('content_hash', models.CharField(blank=True, default='', max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='syllabus_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='syllabustemplate',
            constraint=models.UniqueConstraint(condition=models.Q(('is_default', True)), fields=('owner',), name='unique_default_syllabus_template_per_owner'),
        ),
    ]
