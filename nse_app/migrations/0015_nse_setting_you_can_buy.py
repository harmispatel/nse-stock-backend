# Generated by Django 4.1.5 on 2023-03-13 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0014_pcr_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='nse_setting',
            name='you_can_buy',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
