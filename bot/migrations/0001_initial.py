# Generated by Django 4.0.3 on 2022-04-06 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('name', models.CharField(max_length=25)),
                ('surname', models.CharField(max_length=25)),
                ('phone', models.CharField(blank=True, max_length=12, null=True, unique=True)),
                ('subscriptions', models.JSONField(blank=True, null=True)),
            ],
        ),
    ]