import base64

from djoser.serializers import UserSerializer
from django.core.files.base import ContentFile
from rest_framework import serializers

from users.models import User
from recipes.models import (
    Tag, Ingredient, Recip,
    Favorite, RecipIngredient
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            _format, img_str = data.split(';base64,')
            ext = _format.split('/')[-1]
            data = ContentFile(base64.b64decode(img_str), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Селиализатор модели User"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj: User) -> bool:
        """Проверка подписки."""
        user = self.context.get("request").user
        if user.is_anonymous or (user == obj):
            return False
        return user.follower.filter(following_id=obj.id).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Таг."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recip."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = CustomUserSerializer(
        read_only=True,
    )
    ingredients = IngredientSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Recip
        fields = '__all__'

    def get_is_favorited(self, obj: Recip) -> bool:
        """Проверка - находится ли рецепт в избранном."""
        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False
        return user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj: Recip) -> bool:
        """Проверка - находится ли рецепт в списке покупок."""
        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False
        # Нужно дописать модель корзины.
        # return user.carts.filter(recipe=obj).exists()
        return True
