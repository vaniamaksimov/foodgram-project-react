from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from app.models import Ingredient, Recipe

User = get_user_model()


def if_user_is_anonymous(func):
    def check_user(self, queryset, name, value, *args, **kwargs):
        if self.request.user.is_anonymous:
            return queryset.none()
        return func(self, queryset, name, value, *args, **kwargs)

    return check_user


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(method="name_search")

    class Meta:
        model = Ingredient
        fields = ["name"]

    def name_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(name__iregex=value)


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = filters.NumberFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.NumberFilter(
        method="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
        )

    @if_user_is_anonymous
    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    @if_user_is_anonymous
    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart_items__cart__user=self.request.user)
        return queryset
