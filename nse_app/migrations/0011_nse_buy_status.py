# Generated by Django 4.1.3 on 2022-11-21 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("nse_app", "0010_remove_nse_buy_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="nse",
            name="buy_status",
            field=models.CharField(
                choices=[("BUY", "BUY"), ("SELL", "SELL"), ("empty", "empty")],
                default="empty",
                max_length=50,
            ),
        ),
    ]
