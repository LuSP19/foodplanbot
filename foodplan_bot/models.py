from django.db import models


class Tg_user(models.Model):
    tg_id = models.IntegerField(unique=True, blank=True, null=True)
    name = models.CharField(unique=False, max_length=25)
    surname = models.CharField(unique=False, max_length=25)
    phone = models.CharField(unique=True, max_length=12, blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.name, self.surname)


class User(models.Model):
    tg_user = models.ForeignKey(
        Tg_user,
        on_delete=models.CASCADE,
        related_name='users',
    )
    subscriptions = models.JSONField()

    def __str__(self):
        return '{} {}'.format(self.tg_user.name, self.tg_user.surname)


class Manager(models.Model):
    tg_user = models.ForeignKey(
        Tg_user,
        on_delete=models.CASCADE,
        related_name='managers',
    )

    def __str__(self):
        return self.tg_user.name    
