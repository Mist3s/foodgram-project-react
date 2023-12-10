from django.contrib import admin

from .models import Recip, Tag, Ingredient, Favorite, RecipIngredient


@admin.display(description='Описание')
def trim_field_text(obj):
    """Отображаемый текст не превышает 150 символов."""
    return f"{obj.text[:150]}..."


class IngredientInline(admin.TabularInline):
    model = RecipIngredient
    extra = 1


@admin.register(Recip)
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

