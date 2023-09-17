from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CustomUserViewSet,
                    IngredientViewSet,
                    RecipeViewSet,
                    TagViewSet
                    )

router_v1 = DefaultRouter()
router_v1.register(r'users', CustomUserViewSet, basename='users')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
