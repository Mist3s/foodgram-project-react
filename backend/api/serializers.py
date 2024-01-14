import base64

from djoser.serializers import UserSerializer
from django.core.files.base import ContentFile
from rest_framework import serializers

from users.models import User
from recipes.models import (
    Tag, Ingredient, Recipe, RecipeIngredient
)

MIN_INGREDIENT_AMOUNT = 1


class Base64ImageField(serializers.ImageField):
    """Кастомный тип поля изображений."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            _format, img_str = data.split(';base64,')
            ext = _format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(img_str), name='temp.' + ext
            )
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

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        user = self.context.get("request").user
        if user.is_anonymous or user == obj:
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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте, выходные данные."""
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
    """Сериализатор для модели ингредиентов в рецепте (основной)."""
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recip (GET)."""
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True,
        many=True,
        source='recipe_ingredient'
    )
    author = CustomUserSerializer(
        read_only=True,
    )
    is_favorited = serializers.BooleanField(
        read_only=True,
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
    )
    image = Base64ImageField()

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


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recip (основной)."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientAmountSerializer(
        many=True,
    )
    author = CustomUserSerializer(
        read_only=True,
    )
    image = Base64ImageField()

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

    def validate_ingredients(self, value):
        """Валидация поля ingredients."""
        if not value:
            raise serializers.ValidationError(
                'Нужно добавить хотя бы один ингредиент.'
            )
        for ingredient in value:
            if not int(ingredient.get('amount')) >= MIN_INGREDIENT_AMOUNT:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.'
                )
            if not Ingredient.objects.filter(
                    pk=ingredient.get('id')
            ).exists():
                raise serializers.ValidationError(
                    (f'Ингредиента с id - '
                     f'{ingredient.get("id")}, не существует.')
                )
        id_list = [ingredient.get('id') for ingredient in value]
        if len(id_list) != len(set(id_list)):
            raise serializers.ValidationError(
                'Дублирование ингредиента.'
            )
        return value

    def validate_tags(self, value):
        """Валидация поля tags."""
        if not value:
            raise serializers.ValidationError(
                'Нужно добавить хотя бы один тег.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Дублирование тега.'
            )
        return value

    def to_representation(self, instance):
        """Переопределение сериализатора для выходных данных."""
        return RecipeGetSerializer(
            instance, context=self.context
        ).data

    def create_and_update_objects(self, recipe, ingredients, tags):
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

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.create_and_update_objects(
            recipe=recipe,
            ingredients=ingredients,
            tags=tags
        )

    def update(self, recipe, validated_data):
        """Обновление рецепта"""
        if (not validated_data.get('ingredients')
                or not validated_data.get('tags')):
            raise serializers.ValidationError(
                'Не все обязательные поля заполнены.'
            )
        recipe.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().update(recipe, validated_data)
        return self.create_and_update_objects(
            recipe=recipe,
            ingredients=ingredients,
            tags=tags
        )


class RecipesShortSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe в подписках/корзине."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""
    recipes = serializers.SerializerMethodField()
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

    def get_recipes_count(self, obj):
        """Подсчет количества рецептов у пользователя."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Ограничение количества выводимых рецептов, в подписках."""
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit := self.context['request'].GET.get(
                'recipes_limit'
        ):
            queryset = queryset[:int(recipes_limit)]
        return RecipesShortSerializer(
            queryset,
            many=True
        ).data
