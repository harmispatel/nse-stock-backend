# Generated by Django 4.1.5 on 2023-02-09 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0008_alter_live_table_alter_nse_setting_table_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='live',
            table='live_settings',
        ),
        migrations.AlterModelTable(
            name='pcr_option',
            table='pcr_options',
        ),
        migrations.AlterModelTable(
            name='pcr_stock_name',
            table='pcr_stockName',
        ),
        migrations.AlterModelTable(
            name='stock_detail',
            table='stocks_details',
        ),
    ]