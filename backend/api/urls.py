from django.urls import path, include, re_path
from rest_framework import routers

from .views import (
    TagViewSet, IngredientViewSet,
    RecipeViewSet, CartViewSet
)


v1_router = routers.DefaultRouter()
v1_router.register(r'tags', TagViewSet)
v1_router.register(r'ingredients', IngredientViewSet)
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    CartViewSet
)
v1_router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    re_path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
