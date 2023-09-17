from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):

    page_size_query_param = 'limit'


class RecipeSubscribePaginator(PageNumberPagination):
    """Пагинатор для отображения рецептов на странице подписок."""
    page_size_query_param = 'recipe_limit'
    page_size = 3
