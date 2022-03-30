from django.contrib import admin
from django.db.models import fields

from .models import Tg_user, User, Manager


@admin.register(Tg_user)
class Tg_userAdmin(admin.ModelAdmin):
    list_display = (
        'tg_id',
        'name',
        'surname',
        'phone',
    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'tg_user',
    )


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = (
        'tg_user',
    )
