# Generated by Django 4.2.5 on 2023-11-13 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0065_alter_account_lastcoor_alter_account_lastcoordate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='about',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]