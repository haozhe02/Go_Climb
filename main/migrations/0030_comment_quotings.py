# Generated by Django 4.2.5 on 2023-10-15 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_alter_account_savedsubtopics'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='quotings',
            field=models.ManyToManyField(blank=True, related_name='quotedBy', to='main.forumpost'),
        ),
    ]
