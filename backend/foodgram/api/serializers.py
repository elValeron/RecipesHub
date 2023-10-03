from drf_extra_fields.fields import Base64ImageField

from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from api.constants import MIN_VALUE, MAX_VALUE_AMOUNT, MAX_VALUE_TIME
from recipes.models import (Ingredient,
                            IngredientForRecipe,
                            Recipe,
                            Tag,
                            Favorite,
                            ShoppingCart)
from users.models import CustomUser, Subscribe


class CustomUserListSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
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
    id = serializers.PrimaryKeyRelatedField(
        source='ingredients_set',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(
                limit_value=MIN_VALUE,
                message='Значение не должно быть меньше 1'
            ),
            MaxValueValidator(
                limit_value=MAX_VALUE_AMOUNT,
                message='Значение слишком велико.'
            )
        ]
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

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):

    author = CustomUserListSerializer(
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
        default='False'
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default='False'
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
"""
    def get_is_favorited(self, obj):
        print(obj)
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )
"""
class RecipeSerializer(RecipeReadSerializer):
    """Сериалайзер модели Recipe."""

    author = CustomUserListSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        validators=[
            UniqueValidator(
                queryset=Tag.objects.all(),
                message='Тэг должен быть уникальным'
            )
        ]
    )
    ingredients = IngredientForRecipeSerializer(
        source='ingredient_list',
        many=True,
        validators=[
            UniqueValidator(
                Ingredient.objects.all(),
                message='Ингредиент должен быть уникальным'
            )
        ]
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(
                limit_value=MIN_VALUE,
                message='Значение не должно быть меньше 1'
            ),
            MaxValueValidator(
                limit_value=MAX_VALUE_TIME,
                message='Слишком большое значение.'
            )
        ]
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
            ingredient_list.append(IngredientForRecipe(
                recipe=recipe,
                ingredients_id=ingredient['ingredients_set'].id,
                amount=ingredient['amount']
                )
            )
        IngredientForRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredient_list')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredient_list')
        instance.ingredients.clear()
        self.create_ingredient(ingredients, instance)
        instance.save()
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = data.get('ingredient_list')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ингредиенты обязательно'
            ) 
        tags = data.get('tags')
        if tags is None or not tags:
            raise serializers.ValidationError(
                'Должен быть выбран минимум 1 тэг'
            )
        if len(set(tags)) < len(tags):
            raise serializers.ValidationError(
                'Тэги должны быть уникальны'
            )
        ingredient_lst = [
            ingredient['ingredients_set'] for ingredient in ingredients
        ]
        if len(set(ingredient_lst)) < len(ingredient_lst):
            raise serializers.ValidationError(
                'Ингредиент должен быть уникальным'
            )
        if not ingredient_lst:
            raise serializers.ValidationError(
                'Должен быть выбран минимум 1 ингредиент.'
            )
        return data
    
    def validate_image(self, value):
        if value is None:
            raise serializers.ValidationError(
                'Загрузите картинку'
            )
        return value
    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance=instance,
            context=self.context
        ).data


class SubscribeListSerializer(CustomUserListSerializer):
    """Сериалайзер модели Subscribe."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
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
        if 'recipes_limit' in request.query_params:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return ShortRecipeSerializer(recipes, many=True).data


class SubscribePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('author', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('author', 'user')
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
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
    def validate_recipe(self, value):
        print(value)
        if not Recipe.objects.get(id=value.id):
            return 'рецепта не существует'
        return value
    
    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор модели ShoppingCart"""
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
