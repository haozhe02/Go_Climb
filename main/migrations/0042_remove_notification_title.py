# Generated by Django 4.2.5 on 2023-10-19 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_rename_suspended_account_accountsuspended_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='title',
        ),
    ]
