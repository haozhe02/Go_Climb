# Generated by Django 4.2.5 on 2023-11-13 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0064_alter_account_emergencycontact_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='lastCoor',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='lastCoorDate',
            field=models.TextField(blank=True, null=True),
        ),
    ]