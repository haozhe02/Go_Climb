# Generated by Django 4.2.5 on 2023-10-09 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_account_totaldistance_account_totalroute'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='achievement',
            name='users',
        ),
        migrations.AddField(
            model_name='account',
            name='achievements',
            field=models.ManyToManyField(to='main.achievement'),
        ),
    ]
