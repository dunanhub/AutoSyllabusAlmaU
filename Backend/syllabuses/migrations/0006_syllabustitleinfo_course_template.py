from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabuses', '0005_syllabustitleinfo_school_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabustitleinfo',
            name='courseType',
            field=models.CharField(blank=True, default='default', max_length=64),
        ),
        migrations.AddField(
            model_name='syllabustitleinfo',
            name='templateId',
            field=models.CharField(blank=True, default='default-almau-syllabus', max_length=64),
        ),
    ]
