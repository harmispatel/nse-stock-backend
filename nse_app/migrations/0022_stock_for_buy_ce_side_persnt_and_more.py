# Generated by Django 4.1.5 on 2023-03-23 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0021_extra_setting'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock_for_buy',
            name='CE_side_persnt',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='stock_for_buy',
            name='PE_side_persnt',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
