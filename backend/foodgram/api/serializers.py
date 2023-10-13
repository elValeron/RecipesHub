from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from foodgram.constants import MAX_VALUE_AMOUNT, MAX_VALUE_TIME, MIN_VALUE
from recipes.models import (Ingredient,
                            IngredientForRecipe,
                            Favorite,
                            Recipe,
                            ShoppingCart,
                            Tag)
from users.models import User, Subscribe


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.subscriber.filter(
                author=obj
            ).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер модели Tag."""

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления ингредиентов к рецепту."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE_AMOUNT,
        error_messages={
            'max_value':
                f'Значение не должно быть больше {MAX_VALUE_AMOUNT}',
            'min_value':
                f'Значение не должно быть меньше {MIN_VALUE}'
        }
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class IngredientForRecipeGetSerializer(IngredientForRecipeSerializer):
    """Сериалайзер сквозной модели для отображения в рецепте."""
    id = serializers.IntegerField(
        source='ingredients.id'
    )
    name = serializers.CharField(
        source='ingredients.name'
    )
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit',
    )

    class Meta:
        model = IngredientForRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        read_only_fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображении краткого описания рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения модели Recipes"""
    author = UserSerializer(
        read_only=True,
    )
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    image = Base64ImageField()
    ingredients = IngredientForRecipeGetSerializer(
        source='ingredient_list',
        many=True
    )
    is_favorited = serializers.BooleanField(
        read_only=True,
        default=0
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=0
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeSerializer(RecipeReadSerializer):
    """Сериалайзер модели Recipe."""

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientForRecipeSerializer(
        many=True,)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE_TIME,
        error_messages={
            'max_value':
                f'Значение не должно быть больше {MAX_VALUE_TIME}',
            'min_value':
                f'Значение не должно быть меньше {MIN_VALUE}'
        }
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        extra_kwargs = {
            'ingredients': {
                'required': True,
                'allow_blank': False
            },
            'tags': {
                'required': True,
                'allow_blank': False
            }
        }

    @staticmethod
    def create_ingredient(ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(
                IngredientForRecipe(
                    recipe=recipe,
                    ingredients=ingredient['id'],
                    amount=ingredient['amount']
                )
            )
        IngredientForRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredient(ingredients, instance)
        instance.save()
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ингредиенты обязательно'
            )
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Должен быть выбран минимум 1 тэг'
            )
        if len(set(tags)) < len(tags):
            raise serializers.ValidationError(
                'Тэги должны быть уникальны'
            )
        ingredient_lst = [
            ingredient['id'] for ingredient in ingredients
        ]

        if len(set(ingredient_lst)) < len(ingredient_lst):
            raise serializers.ValidationError(
                'Ингредиент должен быть уникальным'
            )
        if not ingredients:
            raise serializers.ValidationError(
                'Должен быть выбран минимум 1 ингредиент.'
            )
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Загрузите картинку'
            )
        return value

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance=instance,
            context=self.context
        ).data


class SubscribeListSerializer(UserSerializer):
    """Сериалайзер модели Subscribe."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass
        return ShortRecipeSerializer(recipes, many=True).data


class SubscribePostSerializer(serializers.ModelSerializer):
    """Сериалайзер модели Subscribe"""
    class Meta:
        model = Subscribe
        fields = ('author', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписаны на автора.'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        author = data['author']
        if request.user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя!'
            )
        return data

    def to_representation(self, instance):
        return SubscribeListSerializer(
            instance.author,
            context=self.context
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер валидации Избранного"""

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже есть в избранном!'
            )
        ]

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор валидации корзины покупок"""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже есть в списке покупок'
            )
        ]

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context=self.context
        ).data
