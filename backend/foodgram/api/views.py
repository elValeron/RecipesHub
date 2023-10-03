from http import HTTPStatus
from django.db.models import F, OuterRef, Exists, When, Case, Subquery
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,)
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import IngredientsFilterSet, RecipeFilterSet
from api.pagination import CustomPaginator
from api.permissions import IsAuthorOrReadOnly
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
                            Recipe,
                            ShoppingCart,
                            Tag)
from users.models import CustomUser, Subscribe


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPaginator
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
        """Создание подписки"""
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
        """Удаление подписки"""
        author = get_object_or_404(CustomUser, id=id)
        subscribe = Subscribe.objects.filter(
            author_id=author.id,
            user=request.user.id
        )
        if subscribe.exists():
            subscribe.delete()
            msg = f'{author.username} удалён из подписок.'
            return Response(
                    data={'detail': msg},
                    status=HTTPStatus.NO_CONTENT
                )
        msg = 'Вы не были подписаны на пользователя'
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
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = IngredientsFilterSet
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет работы с тэгами"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    

class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами"""

    queryset = Recipe.objects.all().select_related(
        'author'
        ).prefetch_related(
            'tags',
            'ingredients'
        )
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            favorite = Subquery(
                Favorite.objects.filter(
                    user=self.request.user,
                    recipe=OuterRef('pk')
                )
            )
            shopping = Subquery(
                ShoppingCart.objects.filter(
                    user=self.request.user,
                    recipe=OuterRef('pk')
                )
            )
            queryset = queryset.annotate(
                is_favorited=Exists(favorite),
                is_in_shopping_cart=Exists(shopping)
            )
            return queryset
        queryset = queryset.annotate(
            is_favorited=Case(
                When(
                    favorite__user=self.request.user.is_anonymous,
                    then=False
                ),
                default=False,
                
            ),
            is_in_shopping_cart=Case(
                When(
                    shoppingcart=self.request.user.is_anonymous,
                    then=False
                ),
                default=False,
            )
        )
        return queryset

    def get_permissions(self):
        if self.request.user.is_authenticated:
            return (IsAuthorOrReadOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeSerializer

    @staticmethod
    def favorite_cart_add(serializer_class, request, pk):
        """Статик добавления рецепта в избранное/корзину."""
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(
                data={'detail': 'Рецепта не существует'},
                status=HTTPStatus.BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, pk=pk)

        serializer = serializer_class(
            data={
                'recipe': recipe.id,
                'user': request.user.id
            },
            context={
                'request': request
            },
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                data=serializer.data,
                status=HTTPStatus.CREATED
                )
        return Response(data=serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @staticmethod
    def favorite_cart_delete(cls, request, pk):
        """Статик удаления рецепта из избранного/корзины"""
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = cls.objects.filter(
            recipe=recipe.id,
            user=request.user.id
        )
        if obj.exists():
            obj.delete()
            msg = f'{recipe.name} удалён из {cls._meta.verbose_name_plural}'
            return Response(
                        data={'detail': msg},
                        status=HTTPStatus.NO_CONTENT
                    )
        msg = f'Рецепт не был добавлен в {cls._meta.verbose_name_plural}'
        return Response(
            data={'detail': msg},
            status=HTTPStatus.BAD_REQUEST
        )

    @action(
        methods=(
            'post',
        ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """Action для добавления рецепта в избранное."""
        return self.favorite_cart_add(FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        return self.favorite_cart_delete(Favorite, request, pk)

    @action(
        methods=(
            'post',
        ),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Action для добавления рецепта в список покупок."""
        return self.favorite_cart_add(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        """Удаление рецепта из списка покупок."""
        return self.favorite_cart_delete(ShoppingCart, request, pk)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Action для выгрузки списка покупок."""
        ingredients = Ingredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'name',
            'measurement_unit',
        ).annotate(
            recipe__shoppingcart__user=F('ingredient_list__amount')
        ).order_by(
            'name'
        )
        shopping_cart = [
            f'Cписок покупок {request.user}: \r'
        ]
        file_name = f'{request.user}_shopping_cart.txt'
        for ingredient in ingredients:
            shopping_cart.append(
                ' '.join(map(
                    str,
                    ingredient.values()
                    )
                ) + '\n'
            )
        response = FileResponse(shopping_cart, content_type='text')
        response['Content-Disposition'] = (
            'attachment; filename={file_name}'.format(file_name=file_name)
        )
        return response
