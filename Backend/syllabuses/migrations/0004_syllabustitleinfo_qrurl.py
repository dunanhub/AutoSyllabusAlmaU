from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabuses', '0003_syllabus_pdf_processing'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabustitleinfo',
            name='qrUrl',
            field=models.URLField(blank=True, default=''),
        ),
    ]
