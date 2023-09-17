from django.contrib import admin

from .models import (Ingredient,
                     IngredientForRecipe,
                     Favorite,
                     Recipe,
                     Tag,
                     ShoppingCart)


class IngredientForRecipeAdmin(admin.TabularInline):
    """Связывающая модель рецепт-ингредиент для админ панели."""

    model = IngredientForRecipe
    min_num = 1
    extra = 0


class IngridientsAdmin(admin.ModelAdmin):
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


class TagAdmin(admin.ModelAdmin):
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


class RecipeAdmin(admin.ModelAdmin):
    """Модель рецепта для админ панели."""

    inlines = (IngredientForRecipeAdmin,)
    list_display = (
        'author',
        'pk',
        'name',
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


class FavoriteAdmin(admin.ModelAdmin):
    """Модель Favorite для админ панели"""

    fields = (
        'recipe',
        'author',
    )
    readonly_fields = (
        'recipe',
        'author',
    )
    search_fields = (
        'author',
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    """Модель ShoppingCart для админ панели."""

    fields = (
        'pk',
        'recipe',
        'owner',
    )
    readonly_fields = (
        'pk',
        'recipe',
        'owner',
    )
    search_fields = (
        'owner',
        'recipe',
    )


admin.site.register(Recipe, RecipeAdmin,)
admin.site.register(Ingredient, IngridientsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
