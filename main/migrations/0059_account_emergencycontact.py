# Generated by Django 4.2.5 on 2023-10-30 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0058_alter_chat_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='emergencyContact',
            field=models.CharField(max_length=150, null=True),
        ),
    ]