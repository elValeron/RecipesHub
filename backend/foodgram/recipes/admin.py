from django.contrib.admin import ModelAdmin, register, TabularInline, site
from django.contrib.auth.models import Group

from .constants import MIN_VALUE
from .models import (Ingredient,
                     IngredientForRecipe,
                     Favorite,
                     Recipe,
                     Tag,
                     ShoppingCart)


class IngredientForRecipeAdmin(TabularInline):
    """Связывающая модель рецепт-ингредиент для админ панели."""

    model = IngredientForRecipe
    min_num = MIN_VALUE
    extra = 0


@register(Ingredient)
class IngridientsAdmin(ModelAdmin):
    """Модель ингредиентов для админ панели."""

    list_display = (
        'measurement_unit',
        'name',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )


@register(Tag)
class TagAdmin(ModelAdmin):
    """Модель тэга для админ панели."""
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    search_fields = (
        'slug',
    )
    list_filter = (
        'name',
    )
    empty_value_display = '-empty-'


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Модель рецепта для админ панели."""

    inlines = (IngredientForRecipeAdmin,)
    list_display_links = (
        'pk',
        'name',
    )
    list_display = (
        'author',
        'pk',
        'name',
        'get_ingredients',
        'in_favorites',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )
    empty_value_display = '-empty-'

    def in_favorites(self, obj):
        return obj.favorite_set.count()

    def get_ingredients(self, obj):
        ingredient = [i.name for i in obj.ingredients.all()]
        return ingredient

    get_ingredients.short_description = 'ингредиенты'
    in_favorites.short_description = 'кол-во добавлений в избранное'


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    """Модель Favorite для админ панели"""

    fields = (
        'recipe',
        'author',
    )
    search_fields = (
        'author',
    )


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    """Модель ShoppingCart для админ панели."""

    fields = (
        'pk',
        'recipe',
        'author',
    )
    search_fields = (
        'author',
        'recipe',
    )


site.unregister(Group)
