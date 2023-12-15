from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import User
from recipes.models import Tag, Ingredient, Recip


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
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(
        read_only=True,
    )
    ingredients = IngredientSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recip
        fields = '__all__'

    def get_is_favorited(self, obj: Recip) -> bool:
        return False

    def get_is_in_shopping_cart(self, obj: Recip) -> bool:
        return False
