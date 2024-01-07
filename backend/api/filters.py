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
    is_favorited = rest_framework.BooleanFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart',
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

    def filter_is_favorited(self, queryset, name, value):
        return self._filter_user_relation(queryset, 'favorite_recipe', value)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._filter_user_relation(queryset, 'cart_recipe', value)

    def _filter_user_relation(self, queryset, relation_name, value):
        if self.request.user.is_anonymous:
            return queryset
        lookup_params = {f'{relation_name}__user': self.request.user}
        return (queryset.filter(**lookup_params)
                if value else queryset.exclude(**lookup_params))

    class Meta:
        model = Recipe
        fields = [
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        ]
