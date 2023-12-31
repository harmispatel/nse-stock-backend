# Generated by Django 4.1.5 on 2023-04-20 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0024_basezone_alter_livedata_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='livedata',
            name='in_basezone',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='basezone',
            name='base_price',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='basezone',
            name='in_basezone',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='basezone',
            name='stop_loss_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
