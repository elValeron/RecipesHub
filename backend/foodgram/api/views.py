import csv
from http import HTTPStatus

from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import IngredientsFilterSet, RecipeFilterSet
from api.pagination import PageNumberPagination
from api.serializers import (CustomUserListSerializer,
                             FavoriteSerializer,
                             IngredientSerializer,
                             RecipeReadSerializer,
                             RecipeSerializer,
                             ShoppingCartSerializer,
                             SubscribeListSerializer,
                             SubscribePostSerializer,
                             TagSerializer)
from recipes.models import (Favorite,
                            Ingredient,
                            IngredientForRecipe,
                            Recipe,
                            ShoppingCart,
                            Tag)
from users.models import CustomUser, Subscribe


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,) #На дебаге пока так!!! НЕЗАБУДЬ УБРАТ!
    pagination_class = PageNumberPagination
    serializer_class = CustomUserListSerializer

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        methods=(
            'post',
        ),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(CustomUser, id=id)

        serializer = SubscribePostSerializer(
            data={
                'author': author.id,
                'user': request.user.id
            },
            context={
                'request': request
            },
            many=False
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.CREATED)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        author = get_object_or_404(CustomUser, id=id)
        subscribe = Subscribe.objects.filter(
            author_id=author.id,
            user=request.user.id
        )
        if subscribe.exists:
            subscribe.delete()
            msg = f'{author.username} удалён из подписок.'
            return Response(
                    data={'detail': msg},
                    status=HTTPStatus.NO_CONTENT
                )
        return Response(HTTPStatus.BAD_REQUEST)

    @action(
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        detail=False
    )
    def subscriptions(self, request):
        """Action для отображения подписок пользователя."""

        queryset = CustomUser.objects.filter(
            publisher__user_id=request.user.id
        )
        page = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            page,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиетов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = IngredientsFilterSet
    search_fields = ('name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет работы с тэгами"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами"""

    queryset = Recipe.objects.select_related(
        'author'
        ).prefetch_related(
            'tags',
            'ingredients'
        )
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet
    filterset_fields = (
        'author',
        'tags',
        'is_favorited',
        'is_in_shopping_cart'
    )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeSerializer

    @staticmethod
    def favorite_cart_add(serializer_class, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        data = {
            'author': user.id,
            'recipe': recipe.id
        }
        serializer = serializer_class(
            data=data,
            context={
                'request': request
            },
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, HTTPStatus.CREATED)
        return Response(serializer.error, HTTPStatus.BAD_REQUEST)

    @staticmethod
    def favorite_cart_delete(cls, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        instance = cls.objects.filter(
            recipe_id=recipe.id,
            user_id=request.user.id
        )
        if instance.exists:
            instance.delete()
            msg = f'{recipe.name} удалён из {cls.Meta.verbose_name_plural}'
            return Response(
                    data={'detail': msg},
                    status=HTTPStatus.NO_CONTENT
                )
        return Response(HTTPStatus.BAD_REQUEST)


    @action(
        methods=(
            'post',
        ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """Action для добавления рецепта в избранное."""
        self.favorite_cart_add(FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def favorite_delete(self, request, id):
        self.favorite_cart_delete(Favorite, request, id)

    @action(
        methods=(
            'post',
        ),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, id):
        """Action для добавления рецепта в список покупок."""
        self.favorite_cart_add(ShoppingCartSerializer, request, id)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, id):
        """Удаление рецепта из списка покупок."""
        self.favorite_cart_delete(ShoppingCart, request, id)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Action для выгрузки списка покупок."""

        ingredients = IngredientForRecipe.objects.filter(
            recipe__shopping__owner=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit',
        )
        shopping_cart = [
            'Cписок покупок {name}:'.format(
                name=request.user.username
            ),
        ]
        file_name = f'{request.user.username}_shopping_cart.csv'
        with open(file_name, 'w', newline='') as file:
            for ingredient in ingredients:
                name = ingredient['ingredients__name']
                unit = ingredient['ingredients__measurement_unit']
                amount = str(ingredient['amount'])
                fields = (name, amount, unit,)
                shopping_cart.append(' '.join(fields))
            writer = csv.writer(file, delimiter='\r')
            writer.writerow(shopping_cart)
            response = FileResponse(shopping_cart, content_type='text')
            response['Content-Disposition'] = (
                'attachment; filename={file_name}'.format(file_name=file_name)
            )
        return response
