from django.db import models
from django.core.validators import MinValueValidator
from users.models import User


class RecipeQuerySet(models.QuerySet):
    """Кастомный QuerySet для модели рецептов."""
    def with_favorited_and_in_cart_status(self, user):
        return self.annotate(
            is_favorited=models.Exists(
                Favorite.objects.filter(
                    recipe=models.OuterRef('pk'),
                    user=user
                )
            ),
            is_in_shopping_cart=models.Exists(
                Cart.objects.filter(
                    recipe=models.OuterRef('pk'),
                    user=user
                )
            )
        )


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
        help_text='Укажите название',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг',
        help_text='Укажите слаг',
    )
    color = models.CharField(max_length=7)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Укажите название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Укажите единицу измерения ингредиента',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipe',
        verbose_name='Ингредиент',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
        verbose_name='Тег рецепта',
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
        help_text='Укажите название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
            )
        ],
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления (в минутах)'
    )
    text = models.TextField(
        verbose_name="Описание",
        help_text='Добавьте описание'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Укажите автора'
    )
    objects = models.Manager.from_queryset(
        RecipeQuerySet
    )()

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorites'
        )]


class RecipeIngredient(models.Model):
    """Вспомогательная модель: Рецепт - Ингредиент."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт',
        help_text='Укажите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Ингредиент',
        help_text='Укажите ингредиент'
    )
    amount = models.IntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт - Ингредиент'
        verbose_name_plural = verbose_name
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient'
        )]


class Cart(models.Model):
    """Модель корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipes',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_cart'
        )]
