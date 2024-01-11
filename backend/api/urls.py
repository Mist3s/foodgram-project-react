from django.urls import path, include, re_path
from rest_framework import routers

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    CustomUserViewSet
)


v1_router = routers.DefaultRouter()
v1_router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
v1_router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
v1_router.register(
    'recipes',
    RecipeViewSet,
    basename='recipe'
)
v1_router.register(
    'users',
    CustomUserViewSet,
    basename='users'
)

urlpatterns = [
    path('', include(v1_router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
