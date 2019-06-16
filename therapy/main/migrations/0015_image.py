# Generated by Django 2.2 on 2019-05-07 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_day_daycode'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('imagefile', models.FileField(null=True, upload_to='images/', verbose_name='')),
            ],
        ),
    ]
