# Generated by Django 4.2.5 on 2023-10-26 10:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0049_delete_reactionemoji'),
    ]

    operations = [
        migrations.AddField(
            model_name='postdraft',
            name='angryCount',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='angryReactions',
            field=models.ManyToManyField(blank=True, related_name='reactAngry', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='cryCount',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='cryReactions',
            field=models.ManyToManyField(blank=True, related_name='reactCry', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='laughCount',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='laughReactions',
            field=models.ManyToManyField(blank=True, related_name='reactLaugh', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='likeCount',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='likeReactions',
            field=models.ManyToManyField(blank=True, related_name='reactLike', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='loveCount',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='loveReactions',
            field=models.ManyToManyField(blank=True, related_name='reactLove', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='scareCount',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postdraft',
            name='scareReactions',
            field=models.ManyToManyField(blank=True, related_name='reactScare', to=settings.AUTH_USER_MODEL),
        ),
    ]
