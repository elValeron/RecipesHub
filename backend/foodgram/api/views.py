from http import HTTPStatus

from django.db.models import Exists, OuterRef, Subquery, Sum
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,)

from api.filters import IngredientsFilterSet, RecipeFilterSet
from api.pagination import LimitPaginator
from api.permissions import IsAuthorOrAuthenticadedReadOnly
from api.serializers import (UserSerializer,
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
from users.models import User, Subscribe


class UserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPaginator
    serializer_class = UserSerializer

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
        try:
            User.objects.get(id=id)
        except User.DoesNotExist:
            raise Http404('Пользователя не существует')
        serializer = SubscribePostSerializer(
            data={
                'author': id,
                'user': request.user.id
            },
            context={
                'request': request
            },
            many=False
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        """Удаление подписки"""
        try:
            User.objects.get(id=id)
        except User.DoesNotExist:
            raise Http404('Пользователь не найден')
        subscribe = Subscribe.objects.filter(
            author_id=id,
            user=request.user.id
        )
        if subscribe.exists():
            subscribe.delete()
            msg = f'{id} удалён из подписок.'
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

        queryset = User.objects.filter(
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
    permission_classes = (IsAuthorOrAuthenticadedReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_anonymous:
            return queryset
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

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeSerializer

    @staticmethod
    def favorite_cart_add(serializer_class, request, id):
        """Статик добавления рецепта в избранное/корзину."""

        serializer = serializer_class(
            data={
                'recipe': id,
                'user': request.user.id
            },
            context={
                'request': request
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )

    @staticmethod
    def favorite_cart_delete(cls, request, pk):
        """Статик удаления рецепта из избранного/корзины"""
        try:
            Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            raise Http404('Рецепта не существует')
        obj = cls.objects.filter(
            recipe=pk,
            user=request.user.id
        )
        if obj.exists():
            obj.delete()
            msg = f' удалён из {cls._meta.verbose_name_plural}'
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

    @staticmethod
    def create_shopping_cart(user, ingredients):
        shopping_cart = [
            f'Cписок покупок {user}: \r'
        ]
        file_name = f'{user}_shopping_cart.txt'
        for ingredient in ingredients:
            shopping_cart.append(
                ' '.join(
                    map(
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

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Action для выгрузки списка покупок."""
        ingredients = IngredientForRecipe.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit',
        ).annotate(
            recipe__shoppingcart__user=Sum('amount')
        ).order_by(
            'ingredients__name'
        )
        shopping_cart = [
            f'Cписок покупок {request.user}: \r'
        ]
        file_name = f'{request.user}_shopping_cart.txt'
        for ingredient in ingredients:
            shopping_cart.append(
                ' '.join(
                    map(
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
