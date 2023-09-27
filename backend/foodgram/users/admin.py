from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser, Subscribe


@register(CustomUser)
class UserAdmin(BaseUserAdmin):
    """Модель User для админ-панели"""
    list_display = (
        'username',
        'first_name',
        'last_name',
        'recipe_count',
        'subscriber_count'
    )

    list_filter = (
        'username',
        'email',
    )
    search_fields = (
        'username',
        'email',
    )

    def recipe_count(self, obj):
        return obj.recipes.count()

    def subscriber_count(self, obj):
        return obj.subscriber.count()

    recipe_count.short_description = 'Кол-во рецептов'
    subscriber_count.short_description = 'Кол-во подписчиков'


@register(Subscribe)
class SubscribeAdmin(ModelAdmin):
    """Модель Subscribe для админ-панели"""
    list_display = (
        'pk',
        'user',
        'author',
    )
