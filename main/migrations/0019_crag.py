# Generated by Django 4.2.5 on 2023-10-12 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_alter_account_achievements_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=150)),
                ('region', models.CharField(max_length=150)),
                ('name', models.CharField(max_length=150)),
                ('desc', models.CharField(max_length=150)),
                ('rocktype', models.CharField(max_length=150)),
                ('altitude', models.BigIntegerField(default=0)),
            ],
        ),
    ]