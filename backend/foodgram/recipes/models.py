from pytils.translit import slugify
from django.core.validators import (
                                    RegexValidator,
                                    MinValueValidator,
                                    MaxValueValidator
                                   )
from django.db import models

from users.models import CustomUser
from .vars import models_vars

User = CustomUser


class Ingredient(models.Model):
    """Модель описывающая ингридиенты рецепта."""

    name = models.CharField(
        max_length=100,
        verbose_name=models_vars.ingredient_name,
        unique=True,
    )
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name=models_vars.ingredient_measurement_unit
    )

    class Meta:
        verbose_name = models_vars.ingredient_singular
        verbose_name_plural = models_vars.ingredient_plural

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Модель описывающая Тэги рецепта."""

    name = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=models_vars.tag_title,
        help_text=models_vars.tag_title_help
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name=models_vars.tag_color,
        help_text=models_vars.tag_color_help,
        validators=[RegexValidator(
            regex=models_vars.regex_validate,
            message=models_vars.invalid_hex_message
            )
        ]
    )
    slug = models.SlugField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        verbose_name=models_vars.tag_slug,
        help_text=models_vars.tag_slug_help
    )

    class Meta:
        verbose_name = models_vars.tag_singular
        verbose_name_plural = models_vars.tag_plural

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:60]
        super().save(*args, **kwargs)


class Recipe(models.Model):
    """Модель описывающая рецепт."""

    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=models_vars.recipe_author
    )
    name = models.CharField(
        max_length=128,
        verbose_name=models_vars.recipe_name,
        help_text=models_vars.recipe_name_help
    )
    image = models.ImageField(
        upload_to='recipes/media/',
        verbose_name=models_vars.recipe_image,
        help_text=models_vars.recipe_image_help,
    )
    text = models.CharField(
        max_length=512,
        verbose_name=models_vars.recipe_desc,
        help_text=models_vars.recipe_desc_help,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientForRecipe',
        verbose_name=models_vars.recipe_ingredients,
        help_text=models_vars.recipe_ingredients_help,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        help_text=models_vars.recipe_tag_help,
        verbose_name=models_vars.recipe_tag,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=models_vars.recipe_cooking_time,
        help_text=models_vars.recipe_cooking_time_help,
        validators=[
            MinValueValidator(
                limit_value=1,
                message=models_vars.min_value_cooking_time
            ),
            MaxValueValidator(
                limit_value=400,
                message=models_vars.max_value_cooking_time
            )
        ]
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=models_vars.recipe_created
    )

    class Meta:
        ordering = ['-created']
        verbose_name = models_vars.recipe_singular
        verbose_name_plural = models_vars.recipe_plural

    def __str__(self) -> str:
        return self.name[:15]


class IngredientForRecipe(models.Model):
    """
    Промежуточная модель для связи ингредиента с рецептами.
    """
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_list',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=models_vars.recipe_singular
    )
    ingredients = models.ForeignKey(
        Ingredient,
        related_name='ingredient_list',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=models_vars.ingredient_singular,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name=models_vars.ingredient_quantity,
        help_text=models_vars.qauntity_help_text,
        validators=[
            MinValueValidator(
                limit_value=1,
                message=models_vars.min_value_amount,
            ),
            MaxValueValidator(
                limit_value=9999,
                message=models_vars.max_value_amount
            )
        ]
    )

    class Meta:
        verbose_name = models_vars.ingredient_for_recipe_singular
        verbose_name_plural = models_vars.ingredient_for_recipe_plural
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredients',
                ],
                name='unique_ingredients'
            )
        ]

    def __str__(self):
        return f'{self.ingredients} {self.recipe}'


class Favorite(models.Model):
    """Модель описывающая Избранное."""
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorites',
        verbose_name=models_vars.favorite_recipe,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        User,
        related_name='author',
        verbose_name=models_vars.favorite_author,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-recipe']
        verbose_name = models_vars.favorite_singular
        verbose_name_plural = models_vars.favorite_plural

    def __str__(self) -> str:
        return f'{self.author.username}, {self.recipe.name}'


class ShoppingCart(models.Model):
    """Модель описывающая Корзину покупок"""
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping',
        on_delete=models.CASCADE,
        verbose_name=models_vars.cart_recipes_verbose,
    )
    owner = models.ForeignKey(
        User,
        related_name='owner',
        on_delete=models.CASCADE,
        verbose_name=models_vars.cart_owner_verbose
    )
    comment = models.CharField(
        max_length=500,
        verbose_name=models_vars.cart_comment_verbose,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-recipe']
        verbose_name = models_vars.cart_singular
        verbose_name = models_vars.cart_plural

    def __str__(self):
        return f'{self.owner.username}.'
