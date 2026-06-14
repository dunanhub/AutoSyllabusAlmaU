from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabuses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabus',
            name='pdf_error',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='syllabuses/pdfs/'),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='pdf_generated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='pdf_status',
            field=models.CharField(
                choices=[
                    ('not_generated', 'Not generated'),
                    ('generated', 'Generated'),
                    ('failed', 'Failed'),
                ],
                default='not_generated',
                max_length=16,
            ),
        ),
    ]
