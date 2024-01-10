from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import status, viewsets, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from users.models import Follow, User
from recipes.models import (
    Tag, Ingredient,
    Recipe, Cart,
    Favorite
)
from .filters import IngredientSearchFilter, RecipeSearchFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, CartSerializer,
    SubscriptionsSerializer, RecipesShortSerializer
)
from .pagination import CustomPagination


def create_object_favorite_or_cart(
        model, recipe_id, request, text, serializer
):
    """Добавление рецепта в избранное/корзину."""
    if not (recipe := Recipe.objects.filter(
            id=recipe_id
    ).first()):
        return Response(
            'Рецепт не существует.',
            status=status.HTTP_400_BAD_REQUEST
        )
    if model.objects.filter(
            recipe=recipe, user=request.user
    ).exists():
        return Response(
            f'Рецепт уже в {text}.',
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.create(
        recipe=recipe,
        user=request.user
    )
    serializer = serializer(
        recipe,
        context={
            'request': request
        }
    )
    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )


def delete_object_favorite_or_cart(
        model, recipe, user, text
):
    """Удаление рецепта из избранного/корзины."""
    # if obj := model.objects.filter(
    #     recipe=recipe, user=user
    # ).first():
    #     obj.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    # return Response(
    #     f'Данного рецепта нет в {text}.',
    #     status=status.HTTP_400_BAD_REQUEST
    # )
    favorite = model.objects.filter(
        recipe=recipe, user=user
    )
    if favorite:
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        f'Данного рецепта нет в {text}.',
        status=status.HTTP_400_BAD_REQUEST
    )


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели пользователей.
    С реализованным функционалом подписок."""
    pagination_class = CustomPagination

    @action(
        ['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Вывод информации о текущем пользователи."""
        user = get_object_or_404(
            User,
            email=request.user.email
        )
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=False
    )
    def subscriptions(self, request):
        """Вывод списка подписок пользователя."""
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
        methods=['post'],
        detail=True
    )
    def subscribe(self, request, **kwargs):
        """Создание подписки."""
        user = get_object_or_404(
            User,
            id=kwargs.get('id')
        )
        if request.user == user:
            return Response(
                'Вы пытаетесь подписаться на себя.',
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
                user=request.user,
                following=user
        ).first():
            return Response(
                data='Вы уже подписаны.',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(
            user=request.user,
            following=user
        )
        serializer = SubscriptionsSerializer(
            user,
            context={
                'request': request
            }
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        """Удаление подписки."""
        user = get_object_or_404(
            User,
            id=kwargs.get('id')
        )
        if following := Follow.objects.filter(
            following=user,
            user=request.user
        ).first():
            following.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data='Вы не подписаны на этого пользователя.',
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Таг."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recip.
    С реализованным функционалом избранных рецептом
    и скачивание списка покупок."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    @action(
        methods=['post'],
        detail=True
    )
    def favorite(self, request, **kwargs):
        """Добавление рецепта в избранное."""
        return create_object_favorite_or_cart(
            model=Favorite,
            recipe_id=kwargs.get('pk'),
            request=request,
            text='favorite',
            serializer=RecipesShortSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        """Удаление рецепта из избранного."""
        recipe = get_object_or_404(
            Recipe,
            id=kwargs.get('pk')
        )
        return delete_object_favorite_or_cart(
            model=Favorite,
            recipe=recipe,
            user=request.user,
            text='favorite',
        )

    @action(
        detail=False,
        methods=['get'],
        pagination_class=IsAuthenticated
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в PDF."""
        recipes = Recipe.objects.filter(
            cart_recipe__user=request.user
        )
        ingredients = Ingredient.objects.filter(
            recipe_ingredient__recipe__in=recipes
        )
        queryset_ingredients = ingredients.annotate(
            sum_amount_ingredients=(
                Sum('recipe_ingredient__amount')
            )
        )
        response = HttpResponse(content_type='application/pdf')
        pdfmetrics.registerFont(
            TTFont(
                'FreeSans',
                'static/fonts/FreeSans.ttf'
            )
        )
        pdf_canvas = canvas.Canvas(response)
        text_object = pdf_canvas.beginText(100, 730)
        text_object.setFont('FreeSans', 12)
        text_object.textLine('Список покупок:')
        for ingredient in queryset_ingredients:
            pdf_text = (f'{ingredient.name} '
                        f'({ingredient.measurement_unit}) — '
                        f'{ingredient.sum_amount_ingredients}')
            text_object.textLine(pdf_text)
        pdf_canvas.drawText(text_object)
        pdf_canvas.setTitle('Ваш список покупок')
        pdf_canvas.save()
        return response


class CartViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для модели CART."""
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        serializer.save(
            user=self.request.user,
            recipe=recipe_id
        )

    @action(
        methods=['delete'],
        detail=False
    )
    def delete(self, request, **kwargs):
        """Удаление рецепта из корзины."""
        get_object_or_404(
            Recipe,
            id=kwargs.get('recipe_id')
        )
        instance = Cart.objects.filter(
            user=request.user,
            recipe=kwargs.get('recipe_id')
        )
        if not instance:
            return Response(
                data='Вы не добавляли этот рецепт в список покупок.',
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
