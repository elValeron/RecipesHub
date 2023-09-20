import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import serializers
from api.pagination import RecipeSubscribePaginator
from recipes.models import Ingredient, IngredientForRecipe, Recipe, Tag
from users.models import CustomUser


class Base64ImageField(serializers.ImageField):
    """Модель сериализации поля image"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(UserCreateSerializer):
    """Сериалайзер для регистрации нового пользователя."""
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
        )

    def to_representation(self, instance):
        representation = {
            'username': instance.username,
            'email': instance.email,
            'id': instance.id,
            'first_name': instance.first_name,
            'last_name': instance.last_name
        }
        return representation


class CustomUserListSerializer(UserSerializer):
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
                author=obj,
                user=request.user
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
    id = serializers.IntegerField(source='ingredients_set.id')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class IngredientForRecipeGetSerializer(IngredientForRecipeSerializer):
    """Сериалайзер сквозной модели для отображения в рецепте."""

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

    def to_representation(self, instance):
        if instance is not None and instance.id is not None:
            representation = {
                'id': instance.ingredients.id,
                'name': instance.ingredients.name,
                'measurement_unit': instance.ingredients.measurement_unit,
                'amount': instance.amount,
            }
            return representation
        else:
            return None


class ShortRecipeSerializer(serializers.ModelSerializer):
    cooking_time = serializers.IntegerField()

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
    image = Base64ImageField(
        required=False,
        allow_null=True
    )
    ingredients = IngredientForRecipeGetSerializer(
        source='ingredient_list',
        many=True
    )
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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

    def get_is_favorited(self, obj) -> bool:
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.in_favorites.filter(
                author=request.user,
                recipe_id=obj.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.shopping.filter(
                owner=request.user,
                recipe_id=obj.id
            ).exists()
        )


class RecipeSerializer(RecipeReadSerializer):
    """Сериалайзер модели Recipe."""

    author = CustomUserListSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )
    ingredients = IngredientForRecipeSerializer(
        source='ingredient_list',
        many=True,
        read_only=False
    )
    image = Base64ImageField(
        required=False,
        allow_null=True
    )
    cooking_time = serializers.IntegerField()

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

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredient_list')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            crnt_ing = Ingredient.objects.get(
                id=ingredient['ingredients_set']['id']
            )
            IngredientForRecipe.objects.create(
                recipe=recipe,
                ingredients=crnt_ing,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.tags.clear()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredient_list')
        instance.ingredients.clear()
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient['ingredients_set']['id']
            )
            IngredientForRecipe.objects.update_or_create(
                recipe=instance,
                ingredients=current_ingredient,
                amount=ingredient['amount']
            )
        instance.save()
        return instance

    def validate(self, data):
        ingredients = data.get('ingredient_list')
        lst = []
        for ingredient in ingredients:
            ingredient_check = ingredient['ingredients_set']['id']
            if ingredient_check in lst:
                raise serializers.ValidationError(
                    'Ингредиент уже есть в рецепте'
                )
            lst.append(ingredient_check)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeReadSerializer(
            instance,
            context={
                'request': request
            }
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
        recipes = obj.recipes.all()[:int(3)]
        paginator = RecipeSubscribePaginator()
        pages = paginator.paginate_queryset(recipes, request)
        return ShortRecipeSerializer(pages, many=True).data
