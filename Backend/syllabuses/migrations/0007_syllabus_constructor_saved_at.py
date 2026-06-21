from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabuses', '0006_syllabustitleinfo_course_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabus',
            name='constructor_saved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
