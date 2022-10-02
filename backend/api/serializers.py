from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from app.models import Ingridient, Recipe, RecipeIngridient, Tag
from users.models import Subscription
from core.serializers import Base64ImageField
from djoser.serializers import UserSerializer


User = get_user_model()


class UserMeSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return (
            False
            if user.is_anonymous
            else Subscription.objects.filter(user=user, author=obj).exists()
        )


class RecipeIngridientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingridient.id")
    name = serializers.ReadOnlyField(source="ingridient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingridient.measurement_unit"
    )

    class Meta:
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        model = RecipeIngridient


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        model = User

    def get_is_subscribed(self, obj):
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tag


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "measurement_unit")
        model = Ingridient


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    ingridients = RecipeIngridientSerializer(
        source="recipeingridient_set", many=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(allow_null=False)

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingridients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe
        validators = (
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(), fields=("name", "author")
            ),
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return (
            False
            if user.is_anonymous
            else obj.favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return obj.cart_items.exists()


class UserRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = UserRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()
