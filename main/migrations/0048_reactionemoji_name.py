# Generated by Django 4.2.5 on 2023-10-26 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_reactionemoji'),
    ]

    operations = [
        migrations.AddField(
            model_name='reactionemoji',
            name='name',
            field=models.CharField(max_length=150, null=True),
        ),
    ]
