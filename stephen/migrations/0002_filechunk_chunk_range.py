# Generated by Django 4.2.7 on 2023-11-17 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stephen', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='filechunk',
            name='chunk_range',
            field=models.CharField(default='', max_length=100),
        ),
    ]