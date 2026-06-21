from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabuses', '0007_syllabus_constructor_saved_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabus',
            name='render_translation_error',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='render_translation_status',
            field=models.CharField(
                choices=[
                    ('not_translated', 'Not translated'),
                    ('translating', 'Translating'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                ],
                default='not_translated',
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='render_translation_task_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='render_translated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='rendered_content',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='rendered_content_en',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='rendered_content_kz',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='rendered_content_ru',
            field=models.TextField(blank=True, default=''),
        ),
    ]
