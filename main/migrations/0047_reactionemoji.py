# Generated by Django 4.2.5 on 2023-10-26 08:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0046_alter_postdraft_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReactionEmoji',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posts', models.ManyToManyField(blank=True, related_name='reactions', to='main.forumpost')),
                ('users', models.ManyToManyField(blank=True, related_name='reactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
