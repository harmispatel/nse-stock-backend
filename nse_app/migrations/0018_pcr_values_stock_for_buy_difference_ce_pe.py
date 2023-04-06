# Generated by Django 4.1.5 on 2023-03-16 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0017_alter_stock_for_buy_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='pcr_values',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_name', models.CharField(choices=[('NIFTY', 'NIFTY'), ('BANKNIFTY', 'BANKNIFTY')], max_length=50)),
                ('pcr_value', models.FloatField(blank=True, default=0)),
                ('timestamp', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'pcr_values',
            },
        ),
        migrations.AddField(
            model_name='stock_for_buy',
            name='difference_ce_pe',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
