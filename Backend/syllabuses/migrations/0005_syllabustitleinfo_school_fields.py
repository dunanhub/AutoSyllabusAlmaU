from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabuses', '0004_syllabustitleinfo_qrurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabustitleinfo',
            name='schoolId',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='syllabustitleinfo',
            name='schoolName',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
