from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabuses', '0009_syllabus_ai_fill'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabus',
            name='pdf_file_ru',
            field=models.FileField(blank=True, null=True, upload_to='syllabuses/pdfs/'),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='pdf_file_kz',
            field=models.FileField(blank=True, null=True, upload_to='syllabuses/pdfs/'),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='pdf_file_en',
            field=models.FileField(blank=True, null=True, upload_to='syllabuses/pdfs/'),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='docx_file_ru',
            field=models.FileField(blank=True, null=True, upload_to='syllabuses/docx/'),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='docx_file_kz',
            field=models.FileField(blank=True, null=True, upload_to='syllabuses/docx/'),
        ),
        migrations.AddField(
            model_name='syllabus',
            name='docx_file_en',
            field=models.FileField(blank=True, null=True, upload_to='syllabuses/docx/'),
        ),
    ]
