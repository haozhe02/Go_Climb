# Generated by Django 4.2.5 on 2023-10-09 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_achievement'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='totalDistance',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='account',
            name='totalRoute',
            field=models.BigIntegerField(default=0),
        ),
    ]
