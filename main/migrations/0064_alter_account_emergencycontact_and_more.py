# Generated by Django 4.2.5 on 2023-11-13 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_crag_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='emergencyContact',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='emergencyContactName',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
