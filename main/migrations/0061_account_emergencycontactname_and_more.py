# Generated by Django 4.2.5 on 2023-11-08 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0060_account_lastcoor_account_lastcoordate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='emergencyContactName',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='emergencyContact',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
