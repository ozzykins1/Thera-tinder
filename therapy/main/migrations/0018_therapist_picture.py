# Generated by Django 2.2 on 2019-05-12 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20190512_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='therapist',
            name='picture',
            field=models.FileField(null=True, upload_to='images/', verbose_name=''),
        ),
    ]
