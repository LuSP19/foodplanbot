from django.contrib import admin

from .models import User


@admin.register(User)
class Tg_userAdmin(admin.ModelAdmin):
    list_display = (
        'tg_id',
        'name',
        'surname',
        'phone',
    )
