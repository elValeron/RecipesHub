from django.contrib.admin import (display,
                                  ModelAdmin,
                                  register,
                                  TabularInline,
                                  site)
from django.contrib.auth.models import Group

from foodgram.constants import MIN_VALUE
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
        'name',
        'measurement_unit',
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

    @display(description='в избранном')
    def in_favorites(self, obj):
        return obj.favorite_set.count()

    @display(description='ингредиенты')
    def get_ingredients(self, obj):
        return [ingredient.name for ingredient in obj.ingregients.all()]


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    """Модель Favorite для админ панели"""

    fields = (
        'recipe',
        'user',
    )
    search_fields = (
        'user',
    )


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    """Модель ShoppingCart для админ панели."""

    fields = (
        'pk',
        'recipe',
        'user',
    )
    search_fields = (
        'user',
        'recipe',
    )


site.unregister(Group)
