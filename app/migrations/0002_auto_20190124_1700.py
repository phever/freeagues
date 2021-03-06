# Generated by Django 2.1.5 on 2019-01-25 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='format',
            field=models.CharField(choices=[('LEG', 'Legacy'), ('MOD', 'Modern'), ('CEDH', 'Competitive EDH')], max_length=5),
        ),
        migrations.AlterField(
            model_name='league',
            name='format',
            field=models.CharField(choices=[('LEG', 'Legacy'), ('MOD', 'Modern'), ('CEDH', 'Competitive EDH')], max_length=5),
        ),
    ]
