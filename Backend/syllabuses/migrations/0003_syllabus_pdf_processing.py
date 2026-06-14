from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabuses', '0002_syllabus_pdf_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabus',
            name='pdf_task_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='syllabus',
            name='pdf_status',
            field=models.CharField(
                choices=[
                    ('not_generated', 'Not generated'),
                    ('processing', 'Processing'),
                    ('generated', 'Generated'),
                    ('failed', 'Failed'),
                ],
                default='not_generated',
                max_length=16,
            ),
        ),
    ]
