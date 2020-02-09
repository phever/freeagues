# Generated by Django 2.1.5 on 2019-01-27 00:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20190125_0052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='format',
            field=models.CharField(choices=[('MOD', 'Modern'), ('CEDH', 'Competitive EDH'), ('LEG', 'Legacy')], max_length=5),
        ),
        migrations.AlterField(
            model_name='eventresult',
            name='date',
            field=models.DateField(default=datetime.date(2019, 1, 26)),
        ),
        migrations.AlterField(
            model_name='league',
            name='format',
            field=models.CharField(choices=[('MOD', 'Modern'), ('CEDH', 'Competitive EDH'), ('LEG', 'Legacy')], max_length=5),
        ),
        migrations.AlterField(
            model_name='player',
            name='first',
            field=models.CharField(default='Blank', max_length=50),
        ),
        migrations.AlterField(
            model_name='player',
            name='last',
            field=models.CharField(default='NoName', max_length=50),
        ),
    ]