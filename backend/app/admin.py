from django.contrib import admin

from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Tag,
)


class RecipeTagInLine(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class TagModelsAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name",)


class IngredientModelsAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


class RecipeModelsAdmin(admin.ModelAdmin):
    readonly_fields = ("times_in_favorite",)
    list_display = ("name", "author")
    search_fields = ("name", "author")
    list_filter = ("name", "author", "tags__name")
    inlines = (RecipeTagInLine, RecipeIngredientInLine)

    def times_in_favorite(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj.id).count()


class FavoriteRecipeModelsAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")


admin.site.register(Tag, TagModelsAdmin)
admin.site.register(Ingredient, IngredientModelsAdmin)
admin.site.register(Recipe, RecipeModelsAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeModelsAdmin)
