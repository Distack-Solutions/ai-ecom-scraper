# Generated by Django 4.2.17 on 2024-12-05 17:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('scraper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductAIVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='AI Generated Title')),
                ('expanded_description', models.TextField(verbose_name='Expanded Description')),
                ('short_description', models.TextField(verbose_name='Short Description')),
                ('meta_description', models.CharField(max_length=255, verbose_name='Meta Description')),
                ('focus_keyphrase', models.CharField(max_length=255, verbose_name='Focus Keyphrase')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ai_version', to='scraper.product', verbose_name='Product')),
            ],
            options={
                'verbose_name': 'Product AI Version',
                'verbose_name_plural': 'Product AI Versions',
            },
        ),
    ]
