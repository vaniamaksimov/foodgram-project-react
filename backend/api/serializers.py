from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
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
        method_name='is_subscribed',
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

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("recipeingredient_set")
        recipe = Recipe.objects.create(**validated_data)
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

    def update(self, instance, validated_data):
        instance.recipetag_set.all().delete()
        instance.recipeingredient_set.all().delete()
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        if "tags" in validated_data:
            tags_data = validated_data.pop("tags")
            for tag in tags_data:
                current_tag = Tag.objects.get(id=tag.id)
                RecipeTag.objects.create(recipe=instance, tag=current_tag)
        if "recipeingredient_set" in validated_data:
            ingredients_data = validated_data.pop("recipeingredient_set")
            for ingredient in ingredients_data:
                current_ingredient = Ingredient.objects.get(
                    id=ingredient["ingredient"].id
                )
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=current_ingredient,
                    amount=ingredient["amount"],
                )
        instance.save()
        return instance

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("Укажите ингридиенты")
        return value

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("Укажите теги")
        return value


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
