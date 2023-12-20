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


class RecipIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""
    id = serializers.IntegerField(
        source='ingredient.id'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )

    class Meta:
        model = RecipIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipIngredient
        fields = ('id', 'amount')


class RecipGetSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recip."""
    tags = TagSerializer(many=True)
    ingredients = RecipIngredientSerializer(
        read_only=True,
        many=True,
        source='recip_ingredient'
    )
    author = CustomUserSerializer(
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Recip
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

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


class RecipSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recip."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientAmountSerializer(many=True)
    author = CustomUserSerializer(
        read_only=True,
    )
    image = Base64ImageField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Recip
        fields = (
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        return RecipGetSerializer(instance, context=self.context).data

    def add_ingredients_and_tags(self, tags, ingredients, recipe):
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            new_ingredient = RecipIngredient(
                recip=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            ingredients_list.append(new_ingredient)
        RecipIngredient.objects.bulk_create(ingredients_list)
        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recip.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            new_ingredient = RecipIngredient(
                recip=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            ingredients_list.append(new_ingredient)
        RecipIngredient.objects.bulk_create(ingredients_list)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            new_ingredient = RecipIngredient(
                recip=instance,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            ingredients_list.append(new_ingredient)
        RecipIngredient.objects.bulk_create(ingredients_list)
        return instance
