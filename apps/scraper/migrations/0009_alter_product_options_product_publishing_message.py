# Generated by Django 4.2.17 on 2024-12-17 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0008_alter_product_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('-id',), 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AddField(
            model_name='product',
            name='publishing_message',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
