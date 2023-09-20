import csv
from http import HTTPStatus

from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.http import HttpResponse

from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from api.permissions import IsAdminOrReadOnly
from api.serializers import (IngredientSerializer,
                             RecipeReadSerializer,
                             RecipeSerializer,
                             ShortRecipeSerializer,
                             SubscribeListSerializer,
                             TagSerializer,
                             )
from recipes.models import (Favorite,
                            Ingredient,
                            IngredientForRecipe,
                            Recipe,
                            ShoppingCart,
                            Tag,
                            )
from users.models import CustomUser, Subscribe


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = CustomUser.objects.all()

    @action(
        methods=(
            'get',
            'put',
            'patch',
            'delete'
        ),
        detail=False,
        permission_classes=(IsAdminOrReadOnly,)
    )
    def me(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            message = 'Вы не авторизованы'
            return Response(
                data={'detail': message},
                status=HTTPStatus.BAD_REQUEST
            )
        if request.method == 'DELETE':
            self.permission_classes = (IsAdminOrReadOnly,)
            message = 'Недостаточно прав.'
            return Response(
                data={'error': message},
                status=HTTPStatus.BAD_REQUEST
            )
        return super().me(request)

    @action(
        methods=(
            'post',
            'delete',
        ),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(CustomUser, id=id)
        if request.method == 'POST':
            if request.user == author:
                msg = 'Нельзя подписаться на себя'
                return Response(
                    data={'detail': msg},
                    status=HTTPStatus.BAD_REQUEST)
            elif Subscribe.objects.filter(
                author=author,
                user=request.user
            ):
                msg = f'Вы уже подписаны на {author.username}'
                return Response(
                    data={
                        'detail': msg
                    },
                    status=HTTPStatus.BAD_REQUEST
                )
            Subscribe.objects.create(
                author=author,
                user=request.user
            )
            serializer = SubscribeListSerializer(
                author,
                context={
                    'request': request
                },
                many=False
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            if author.id in request.user.subscriber.values_list(
                'author_id',
                flat=True
            ):
                Subscribe.objects.filter(
                    author=author,
                    user=request.user
                ).delete()
                msg = f'{author.username} удалён из подписок.'
                return Response(
                    data={'detail': msg},
                    status=HTTPStatus.NO_CONTENT
                )
            msg = f'Вы не были подписаны на {author.username}'
            return Response(
                data={'detail': msg},
                status=HTTPStatus.BAD_REQUEST
            )

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
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name')
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет работы с тэгами"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами"""

    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags')

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited', None)
        if is_favorited is not None:
            queryset = queryset.filter(
                in_favorites__author=self.request.user,
            )
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart',
            None
        )
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(
                shopping__owner=self.request.user
            )
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeSerializer

    @action(
        methods=[
            'post',
            'delete'
        ],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """Action для добавления рецепта в избранное."""

        recipe = get_object_or_404(Recipe, id=pk)
        favorite_list = request.user.author.values_list(
            'recipe__id',
            flat=True
        )
        if request.method == 'POST':
            if recipe.id in favorite_list:
                message = f'{recipe.name}, уже есть в избранном'
                return Response(
                    data={'details': message},
                    status=HTTPStatus.BAD_REQUEST
                )
            favorite, created = Favorite.objects.get_or_create(
                recipe_id=recipe.id,
                author_id=request.user.id
            )
            serializer = ShortRecipeSerializer(
                favorite.recipe,
                many=False
            )
            return Response(serializer.data)

        if request.method == 'DELETE':
            if recipe.id not in favorite_list:
                message = f'{recipe.name} не добавлен в избранное'
                return Response(
                    data={'details': message},
                    status=HTTPStatus.BAD_REQUEST
                )
            favorite = Favorite.objects.get(
                author_id=request.user.id,
                recipe_id=recipe.id
            )
            favorite.delete()
            message = f'{recipe.name} удалён из избранного.'
            return Response(
                data={'details': message},
                status=HTTPStatus.NO_CONTENT
            )

    @action(
        methods=(
            'post',
            'delete',
        ),
        detail=True,
        permission_classes=(IsAuthenticated,)

    )
    def shopping_cart(self, request, pk):
        """Action для добавления рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart_list = request.user.owner.values_list(
            'recipe__id',
            flat=True
        )
        if request.method == 'POST':
            if recipe.id in shopping_cart_list:
                message = f'{recipe.name} уже есть в списке покупок'
                return Response(
                    data={'details': message},
                    status=HTTPStatus.BAD_REQUEST
                )
            ShoppingCart.objects.get_or_create(
                recipe=recipe,
                owner=request.user
            )
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            if not shopping_cart_list:
                message = 'Список покупок пуст'
                return Response(data={'details': message})
            elif recipe.id not in shopping_cart_list:
                message = f'{recipe.name} нет в списке покупок'
                return Response(
                    data={'details': message},
                    status=HTTPStatus.BAD_REQUEST
                )
            shopping_cart = ShoppingCart.objects.filter(
                recipe_id=recipe.id
            )
            shopping_cart.delete()
            message = f'{recipe.name} удален из списка покупок'
            return Response(
                data={'details': message},
                status=HTTPStatus.NO_CONTENT
            )

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
            'amount'
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
            response = HttpResponse(shopping_cart, content_type='text/csv')
            response['Content-Disposition'] = (
                'attachment; filename={file_name}'.format(file_name=file_name)
            )
        return response
