from django_filters import rest_framework

from recipes.models import Ingredient, Recipe, Tag


class IngredientSearchFilter(rest_framework.FilterSet):
    """Фильтрация для модели ингредиентов."""
    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeSearchFilter(rest_framework.FilterSet):
    """Фильтрация для модели рецептов."""
    is_favorited = rest_framework.BooleanFilter()
    is_in_shopping_cart = rest_framework.BooleanFilter()
    author = rest_framework.NumberFilter(
        field_name='author__id'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = [
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        ]
