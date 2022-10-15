from email.policy import default
from pprint import pprint
from attr import attr
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from djoser.serializers import UserSerializer
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from app.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from core.serializers import Base64ImageField
from users.models import Subscription

User = get_user_model()


class UserMeSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

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


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed',
        read_only=True,
    )

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
        user = self.context["request"].user
        return (
            False
            if user.is_anonymous
            else Subscription.objects.filter(user=user, author=obj).exists()
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        model = RecipeIngredient


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )

    class Meta:
        fields = (
            "id",
            "amount",
        )
        model = RecipeIngredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "measurement_unit")
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    ingredients = RecipeIngredientSerializer(
        source="recipeingredient_set",
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited',
        read_only=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart',
        read_only=True,
    )
    image = Base64ImageField(allow_null=False, read_only=True)

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
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
        user = self.context["request"].user
        return (
            False
            if user.is_anonymous
            else obj.cart_items.filter(cart__user=user).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(
        source="recipeingredient_set",
        many=True,
        required=True,
        allow_null=False,
    )
    tags = serializers.SlugRelatedField(
        slug_field="id", queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(allow_null=False)

    class Meta:
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )
        model = Recipe

    @staticmethod
    def _create_links(recipe, tags, ingredients):
        for tag in tags:
            current_tag = Tag.objects.get(id=tag.id)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                name=ingredient["ingredient"].name
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient["amount"],
            )
        return recipe

    @staticmethod
    def _get_tags_and_recipeingridients(validated_data):
        tags = validated_data.pop('tags')
        recipeingredients = validated_data.pop('recipeingredient_set')
        return tags, recipeingredients, validated_data

    @transaction.atomic
    def create(self, validated_data):
        tags, recipeingredients, _validated_data = self._get_tags_and_recipeingridients(validated_data=validated_data)
        recipe = Recipe.objects.create(**_validated_data)
        return self._create_links(recipe=recipe, tags=tags, ingredients=recipeingredients)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.recipetag_set.all().delete()
        instance.recipeingredient_set.all().delete()
        tags, recipeingredients, _validated_data = self._get_tags_and_recipeingridients(validated_data=validated_data)
        super().update(instance=instance, validated_data=_validated_data)
        return self._create_links(recipe=instance, tags=tags, ingredients=recipeingredients)

    def validate(self, attrs):
        recipeingredients = attrs.get('recipeingredient_set')
        recipetags = attrs.get('tags')
        if len(recipetags) == 0:
            raise serializers.ValidationError('Укажите теги')
        if len(recipeingredients) == 0:
            raise serializers.ValidationError('Укажите ингридиенты')
        ingredient_list = [ingredient.get('ingredient') for ingredient in recipeingredients]
        for tag in recipetags:
            if recipetags.count(tag) > 1:
                raise serializers.ValidationError('Нельзя добавлять одинаковые теги')
        for _ingredient in ingredient_list:
            if ingredient_list.count(_ingredient) > 1:
                raise serializers.ValidationError('Нельзя добавлять одинаковые игридиенты')     
        return super().validate(attrs)


class UserRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed',
        read_only=True,
    )
    recipes = UserRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count',
        read_only=True,
    )

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


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe
