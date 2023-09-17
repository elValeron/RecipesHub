from django.contrib import admin

from .models import CustomUser, Subscribe


class UserAdmin(admin.ModelAdmin):
    """Модель User для админ-панели"""
    fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password'
    )
    list_filter = (
        'username',
        'email',
    )
    search_fields = (
        'username',
        'email',
    )


class SubscribeAdmin(admin.ModelAdmin):
    """Модель Subscribe для админ-панели"""
    list_display = (
        'pk',
        'user',
        'author',
    )


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
