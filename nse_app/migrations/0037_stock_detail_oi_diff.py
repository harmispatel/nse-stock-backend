# Generated by Django 4.1.5 on 2023-09-12 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0036_alter_stock_detail_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock_detail',
            name='oi_diff',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
