from django.contrib import admin
from .models import (
    Tag,
    Ingridient,
    Recipe,
    RecipeTag,
    RecipeIngridient,
    FavoriteRecipe,
)


# На странице рецепта вывести общее число добавлений этого рецепта в избранное.


class RecipeTagInLine(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngridientInLine(admin.TabularInline):
    model = RecipeIngridient
    extra = 1


class tagmodelsAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name",)


class ingridientmodelsAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


class recipemodelsAdmin(admin.ModelAdmin):
    readonly_fields = ("times_in_favorite",)
    list_display = ("name", "author")
    search_fields = ("name", "author")
    list_filter = ("name", "author", "tags__name")
    inlines = (RecipeTagInLine, RecipeIngridientInLine)

    def times_in_favorite(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj.id).count()


class favoriterecipemodelsAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")


admin.site.register(Tag, tagmodelsAdmin)
admin.site.register(Ingridient, ingridientmodelsAdmin)
admin.site.register(Recipe, recipemodelsAdmin)
admin.site.register(FavoriteRecipe, favoriterecipemodelsAdmin)
