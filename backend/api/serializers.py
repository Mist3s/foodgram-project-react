import base64

from djoser.serializers import UserSerializer
from django.core.files.base import ContentFile
from rest_framework import serializers

from users.models import User, Follow
from recipes.models import (
    Tag, Ingredient, Recipe,
    Favorite, RecipeIngredient, Cart
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

    # def get_recipes(self, obj):
    #     recipes_limit = self.context.get('recipes_limit')
    #     recipes_queryset = obj.recip.all()
    #
    #     if recipes_limit:
    #         recipes_queryset = recipes_queryset[:recipes_limit]
    #
    #     # Передача recipes_limit в контекст RecipesShortSerializer
    #     context = {'recipes_limit': recipes_limit} if recipes_limit else {}
    #     return RecipesShortSerializer(recipes_queryset, many=True, context=context).data


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


class RecipeIngredientSerializer(serializers.ModelSerializer):
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
        model = RecipeIngredient
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
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recip."""
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True,
        many=True,
        source='recipe_ingredient'
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
        model = Recipe
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

    def get_is_favorited(self, obj: Recipe) -> bool:
        """Проверка - находится ли рецепт в избранном."""
        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False
        return user.favorite_recipe.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        """Проверка - находится ли рецепт в списке покупок."""
        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False
        return user.cart_recipe.filter(recipe=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
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
        model = Recipe
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
        return RecipeGetSerializer(instance, context=self.context).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            new_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            ingredients_list.append(new_ingredient)
        RecipeIngredient.objects.bulk_create(ingredients_list)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            new_ingredient = RecipeIngredient(
                recipe=instance,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            ingredients_list.append(new_ingredient)
        RecipeIngredient.objects.bulk_create(ingredients_list)
        return instance


class CartSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return CartGetSerializer(instance, context=self.context).data

    class Meta:
        model = Cart
        exclude = ('user', 'recipe')

    def create(self, validated_data):
        recipe = Recipe.objects.get(
            id=self.context.get('view').kwargs.get('recipe_id')
        )
        return Cart.objects.create(
            user=self.context.get('request').user,
            recipe=recipe
        )

    def validate(self, data):
        """Валидация повторного добавления в корзину."""
        if self.context.get('request').method != 'POST':
            return data
        recipe = Recipe.objects.get(
            id=self.context.get('view').kwargs.get('recipe_id')
        )
        if Cart.objects.filter(
                user=self.context.get('request').user,
                recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину.'
            )
        return data


class CartGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='recipe.id'
    )
    name = serializers.StringRelatedField(
        source='recipe.name'
    )
    image = serializers.ImageField(
        source='recipe.image'
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time'
    )

    class Meta:
        model = Cart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = ('__all__',)


class RecipesShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionsSerializer(CustomUserSerializer):
    recipes = RecipesShortSerializer(
        many=True,
        source='recip'
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj: User) -> int:
        return obj.recip.count()
