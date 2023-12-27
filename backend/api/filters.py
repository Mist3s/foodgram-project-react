from django_filters import rest_framework
from django_filters import AllValuesMultipleFilter

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(rest_framework.FilterSet):
    # Для sqlite istartswith, а для postgresql search.
    name = rest_framework.CharFilter(lookup_expr='search')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeSearchFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    author = AllValuesMultipleFilter(field_name='author__id')

    def bool_filter(self, key, value, queryset, user):
        """Фильтрация для логических ключей."""
        map_dict = {f'{key}__user': user}
        if user.is_anonymous:
            return queryset
        if value is True:
            return queryset.filter(**map_dict)
        return queryset.exclude(**map_dict)

    def filter_is_favorited(self, queryset, name, value):
        return self.bool_filter(
            'favorite_recipes',
            value,
            queryset,
            user=self.request.user
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self.bool_filter(
            'recipe_in_shoplist',
            value,
            queryset,
            user=self.request.user
        )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart']
