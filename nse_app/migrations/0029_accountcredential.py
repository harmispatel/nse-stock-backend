# Generated by Django 4.1.5 on 2023-08-11 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0028_resistancezone_banknifty_resistancezone_nifty_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountCredential',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('apikey', models.CharField(max_length=50)),
                ('password', models.IntegerField()),
                ('t_otp', models.CharField(max_length=50)),
            ],
        ),
    ]
