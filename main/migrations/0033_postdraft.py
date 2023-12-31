# Generated by Django 4.2.5 on 2023-10-16 15:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0032_maintopic_totalview_subtopic_totalview'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostDraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drafts', to='main.subtopic')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drafts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
