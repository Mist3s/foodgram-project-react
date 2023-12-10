from django.db import models
from django.core.validators import MinValueValidator
from users.models import User


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=200,
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
    """Модель ингредиента."""
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


class Recip(models.Model):
    """Модель рецепта."""
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=True,
        through='RecipIngredient',
        related_name='recip',
        verbose_name='Ингредиент',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='recip',
        verbose_name='Тег рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Укажите название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
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
        blank=True,
        verbose_name="Описание",
        help_text='Добавьте описание'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recip',
        verbose_name='Автор',
        help_text='Укажите автора'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recip,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorites'
        )]


class RecipIngredient(models.Model):
    """Вспомогательная модель: Рецепт - Ингредиент."""
    recip = models.ForeignKey(
        Recip,
        on_delete=models.CASCADE,
        related_name='recip_ingredient',
        verbose_name='Рецепт',
        help_text='Укажите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recip_ingredient',
        verbose_name='Ингредиент',
        help_text='Укажите ингредиент'
    )
    amount = models.FloatField(
        validators=[
            MinValueValidator(
                limit_value=0.001,
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт - Ингредиент'
        verbose_name_plural = verbose_name
