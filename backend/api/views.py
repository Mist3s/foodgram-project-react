from rest_framework import status, viewsets, filters, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet

from users.models import Follow, User
from recipes.models import Tag, Ingredient, Recipe, Cart
from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, CartSerializer,
    SubscriptionsSerializer, FollowSerializer
)


class CustomUserViewSet(UserViewSet):
    @action(
        methods=['get'],
        detail=False
    )
    def subscriptions(self, request):
        user = request.user
        following = User.objects.filter(
            following__user=user
        )
        paginate = self.paginate_queryset(following)
        serializer = SubscriptionsSerializer(
            data=paginate,
            many=True,
            context={
                'request': request
            }
        )
        serializer.is_valid()
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True
    )
    def subscribe(self, request, **kwargs):
        following = get_object_or_404(
            User,
            id=kwargs.get('id')
        )
        if (request.method == 'DELETE'
                and User.objects.filter().exists()):
            print(1111)
        if (request.method == 'POST'
                and not Follow.objects.filter(
                    user=request.user,
                    following=following
                ).exists):
            # Follow.objects.create(
            #     user=request.user,
            #     following=following
            # )
            print(2222)
        print(Follow.objects.filter(
                    user=request.user,
                    following=following
                ).exists)
        return Response(status=200)


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


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recip."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    # @action(
    #     detail=False,
    #     methods=['get'],
    # )
    # def download_shopping_cart(self, request):
    #     instance = Cart.objects.get(
    #         user=request.user
    #     )
    #     print(instance)
    #     data = {
    #         'test': 'test'
    #     }
    #     return Response(data, status=status.HTTP_200_OK)


class CartViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для модели CART."""
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        serializer.save(
            user=self.request.user,
            recipe=recipe_id
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        instance = get_object_or_404(
            Cart,
            user=request.user,
            recipe=kwargs.get('recipe_id')
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartDownloadViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    @action(
        detail=False,
        methods=['get'],
    )
    def download_shopping_cart(self, request):
        instance = Cart.objects.get(
            user=request.user
        )
        print(instance)
        data = {
            'test': 'test'
        }
        return Response(data, status=status.HTTP_200_OK)
