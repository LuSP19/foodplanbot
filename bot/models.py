from django.db import models


class User(models.Model):
    tg_id = models.IntegerField(unique=True, blank=True, null=True)
    name = models.CharField(unique=False, max_length=25)
    surname = models.CharField(unique=False, max_length=25)
    phone = models.CharField(unique=True, max_length=12, blank=True, null=True)
    subscriptions = models.JSONField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.name, self.surname)
