from django_filters import rest_framework
from django_filters import AllValuesMultipleFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientSearchFilter(rest_framework.FilterSet):
    # Для sqlite istartswith, а для postgresql search.
    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeSearchFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.BooleanFilter(
        method='filter_boolean_field',
        field_name='favorite_recipes'
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_boolean_field',
        field_name='recipe_in_shoplist'
    )
    author = rest_framework.NumberFilter(
        field_name='author__id'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all()
    )

    def filter_boolean_field(self, queryset, name, value):
        """Универсальный метод для булевой фильтрации."""
        if self.request.user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(
                **{
                    f'{name}__user': self.request.user
                }
            )
        else:
            return queryset.exclude(
                **{
                    f'{name}__user': self.request.user
                }
            )

    class Meta:
        model = Recipe
        fields = [
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        ]
