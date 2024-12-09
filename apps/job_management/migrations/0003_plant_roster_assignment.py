# Generated by Django 4.2 on 2024-02-15 20:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('job_management', '0002_alter_job_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Roster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('start_date', models.DateField(null=True)),
                ('finish_date', models.DateField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'unique_together': {('start_date', 'finish_date')},
            },
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('finish_time', models.TimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.employee')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job_management.job')),
                ('plant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='job_management.plant')),
                ('roster', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_management.roster')),
            ],
        ),
    ]
