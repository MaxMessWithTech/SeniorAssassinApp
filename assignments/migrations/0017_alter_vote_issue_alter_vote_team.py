# Generated by Django 4.2.18 on 2025-03-02 01:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0016_alter_rulesuspension_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='assignments.issue'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='assignments.team'),
        ),
    ]
