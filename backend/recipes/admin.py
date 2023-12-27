from django.contrib import admin

from .models import (
    Recipe, Tag, Ingredient, Favorite,
    RecipeIngredient, Cart
)


@admin.display(description='Описание')
def trim_field_text(obj):
    """Отображаемый текст не превышает 150 символов."""
    mx_len = 150
    if len(obj.text) > mx_len:
        return f"{obj.text[:mx_len]}..."
    return obj.text


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cooking_time', trim_field_text, 'author')
    list_editable = ('name', 'cooking_time')
    list_filter = ('name', 'cooking_time')
    search_fields = ('name', 'cooking_time')
    inlines = [IngredientInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')
    list_editable = ('name', 'color')
    list_filter = ('name', 'color')
    search_fields = ('name', 'color')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


