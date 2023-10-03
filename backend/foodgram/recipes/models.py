from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipes import constants
from users.models import CustomUser


class Ingredient(models.Model):
    """Модель описывающая ингридиенты рецепта."""

    name = models.CharField(
        max_length=constants.MAX_LENGTH,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=constants.MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                name='unit_ingredients_unique',
                fields=[
                    'name',
                    'measurement_unit'
                ]
            )

        ]

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    """Модель описывающая Тэги рецепта."""

    name = models.CharField(
        max_length=constants.MAX_LENGTH,
        unique=True,
        verbose_name='Имя тэга',
    )
    color = ColorField(
        verbose_name='Цвет тэга',
        unique=True
    )
    slug = models.SlugField(
        max_length=constants.MAX_LENGTH,
        unique=True,
        verbose_name='Адрес тэга'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return f'{self.name},{self.slug}'


class Recipe(models.Model):
    """Модель описывающая рецепт."""

    author = models.ForeignKey(
        CustomUser,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=constants.MAX_LENGTH,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='.media/',
        verbose_name='Фото блюда',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientForRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тэги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                limit_value=constants.MIN_VALUE,
                message='Значение не может быть меньше 1.'
            ),
            MaxValueValidator(
                limit_value=constants.MAX_VALUE_TIME,
                message='Значение не может быть больше 400.'
            )
        ]
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return f'Автор {self.author.username} рецепта {self.name}'


class IngredientForRecipe(models.Model):
    """
    Промежуточная модель для связи ингредиента с рецептами.
    """
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_list',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        related_name='ingredient_list',
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Кол-во ингредиента',
        validators=[
            MinValueValidator(
                limit_value=constants.MIN_VALUE,
                message='Значение не может быть меньше 1.'
            ),
            MaxValueValidator(
                limit_value=constants.MAX_VALUE_AMOUNT,
                message='Введите значение не более 100000'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredients',
                ],
                name='ingredients_unique'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.ingredients} {self.amount}'


class AbstractFavoriteCart(models.Model):
    """Базовая модель для Favorite и ShoppingCart"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        ordering = ('-user')
        constraints = [
            models.UniqueConstraint(
                name='%(class)s_unique',
                fields=[
                    'recipe',
                    'user'
                ]
            )
        ]

    def __str__(self) -> str:
        return f'{self.author.username}, {self.recipe.name}'


class Favorite(AbstractFavoriteCart):
    """Модель описывающая Избранное."""

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(AbstractFavoriteCart):
    """Модель описывающая Корзину покупок"""

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
