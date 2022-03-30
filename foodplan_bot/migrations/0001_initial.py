# Generated by Django 4.0.3 on 2022-03-30 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tg_user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('name', models.CharField(max_length=25)),
                ('surname', models.CharField(max_length=25)),
                ('phone', models.CharField(blank=True, max_length=12, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscriptions', models.JSONField()),
                ('tg_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='foodplan_bot.tg_user')),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managers', to='foodplan_bot.tg_user')),
            ],
        ),
    ]
