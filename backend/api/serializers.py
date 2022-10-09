from asyncore import read
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from app.models import Ingridient, Recipe, RecipeIngridient, Tag
from app.models import RecipeTag
from core.serializers import Base64ImageField
from users.models import Subscription

from rest_framework.response import Response

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


class RecipeIngridientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingridient", queryset=Ingridient.objects.all()
    )

    class Meta:
        fields = (
            "id",
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
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    ingridients = RecipeIngridientSerializer(
        source="recipeingridient_set", many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(allow_null=False, read_only=True)

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


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingridients = RecipeIngridientCreateSerializer(
        source="recipeingridient_set", many=True, required=True, allow_null=False
    )
    tags = serializers.SlugRelatedField(slug_field='id', queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(allow_null=False)

    class Meta:
        fields = (
            'ingridients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        model = Recipe

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingridients = validated_data.pop('recipeingridient_set')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag = Tag.objects.get(id=tag.id)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        for ingridient in ingridients:
            current_ingridient = Ingridient.objects.get(name=ingridient['ingridient'].name)
            RecipeIngridient.objects.create(recipe=recipe, ingridient=current_ingridient, amount=ingridient['amount'])
        return recipe

    def update(self, instance, validated_data):
        instance.recipetag_set.all().delete()
        instance.recipeingridient_set.all().delete()
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            for tag in tags_data:
                current_tag = Tag.objects.get(id=tag.id)
                RecipeTag.objects.create(recipe=instance, tag=current_tag)
        if 'recipeingridient_set' in validated_data:
            ingridients_data = validated_data.pop('recipeingridient_set')
            for ingridient in ingridients_data:
                current_ingridient = Ingridient.objects.get(id=ingridient['ingridient'].id)
                RecipeIngridient.objects.create(recipe=instance, ingridient=current_ingridient, amount=ingridient['amount'])
        instance.save()
        return instance

    def validate_ingridients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError('Укажите ингридиенты')
        return value

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError('Укажите теги')
        return value

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


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe
