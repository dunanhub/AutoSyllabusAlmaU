from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabuses', '0008_syllabus_render_translation'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabus',
            name='ai_fill_status',
            field=models.CharField(
                choices=[
                    ('not_started', 'Not started'),
                    ('processing', 'Processing'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                ],
                default='not_started',
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='ai_fill_error',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='ai_fill_task_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='ai_filled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
