# Generated by Django 4.2.18 on 2025-03-19 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0021_remove_kill_video_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='kill',
            name='video_link',
            field=models.URLField(null=True),
        ),
    ]
