# Generated by Django 4.2.5 on 2023-10-26 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_account_badgeposition_account_routesposition'),
    ]

    operations = [
        migrations.AddField(
            model_name='crag',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='crag',
            name='longitude',
            field=models.FloatField(null=True),
        ),
    ]