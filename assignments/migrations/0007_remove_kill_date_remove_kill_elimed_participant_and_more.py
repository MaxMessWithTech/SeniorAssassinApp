# Generated by Django 4.2.18 on 2025-02-15 00:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0006_kill'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kill',
            name='date',
        ),
        migrations.RemoveField(
            model_name='kill',
            name='elimed_participant',
        ),
        migrations.RemoveField(
            model_name='kill',
            name='eliminator',
        ),
        migrations.RemoveField(
            model_name='kill',
            name='target_team',
        ),
    ]
