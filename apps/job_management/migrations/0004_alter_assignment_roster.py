# Generated by Django 4.2 on 2024-02-15 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job_management', '0003_plant_roster_assignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='roster',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='job_management.roster'),
        ),
    ]
