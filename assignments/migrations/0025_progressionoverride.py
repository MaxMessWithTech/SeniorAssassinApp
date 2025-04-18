# Generated by Django 4.2.18 on 2025-04-04 22:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0024_round_min_progression_kill_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgressionOverride',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('issued_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pro_overrides', to='assignments.round')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pro_overrides', to='assignments.team')),
            ],
        ),
    ]
