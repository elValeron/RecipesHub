from django.contrib.admin import ModelAdmin, register, display
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Subscribe


@register(User)
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

    @display(description='Кол-во рецептов')
    def recipe_count(self, obj):
        return obj.recipes.count()

    @display(description='Кол-во подписчиков')
    def subscriber_count(self, obj):
        return obj.subscriber.count()


@register(Subscribe)
class SubscribeAdmin(ModelAdmin):
    """Модель Subscribe для админ-панели"""
    list_display = (
        'pk',
        'user',
        'author',
    )
