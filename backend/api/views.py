from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet

from users.models import Follow, User
from recipes.models import Tag, Ingredient, Recip
from .serializers import TagSerializer, IngredientSerializer, RecipSerializer


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для модели Таг."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # Нужно допилить поисковой фильтр.
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recip."""
    queryset = Recip.objects.all()
    serializer_class = RecipSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )
