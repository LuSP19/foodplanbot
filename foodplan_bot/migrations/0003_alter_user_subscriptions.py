# Generated by Django 4.0.3 on 2022-04-04 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodplan_bot', '0002_remove_user_tg_user_user_name_user_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='subscriptions',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
