import csv

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Tag,
)
from cart.models import Cart, CartItem
from users.models import Subscription

User = get_user_model()


class Command(BaseCommand):
    help = "Заполнение базы данных из CSV файла"

    def handle(self, *args, **options):
        user_processing()
        subscription_processing()
        cart_processing()
        tag_processing()
        ingredient_processing()
        recipe_processing()
        cart_item_processing()
        favoriterecipe_processing()
        print("database was updated")


def user_processing():
    with open(
        settings.CSV_ROOT + "users.csv",
        newline="",
    ) as csvfile:
        users_data = csv.reader(csvfile, delimiter=";")
        for row in users_data:
            if row[0].lower() != "id":
                user = {
                    "password": row[1],
                    "is_superuser": row[3],
                    "is_staff": row[4],
                    "is_active": row[5],
                    "username": row[7],
                    "first_name": row[8],
                    "last_name": row[9],
                    "email": row[10],
                }
                try:
                    add_to_database(object_data=user, model=User)
                except Exception as e:
                    print(e)
    pass


def subscription_processing():
    with open(
        settings.CSV_ROOT + "subscription.csv",
        newline="",
    ) as csvfile:
        subscription_data = csv.reader(csvfile, delimiter=";")
        for row in subscription_data:
            if row[0].lower() != "id":
                subscripion = {
                    "user_id": row[1],
                    "author_id": row[2],
                }
                try:
                    add_to_database(
                        object_data=subscripion, model=Subscription
                    )
                except Exception as e:
                    print(e)
    pass


def cart_processing():
    with open(
        settings.CSV_ROOT + "cart.csv",
        newline="",
    ) as csvfile:
        cart_data = csv.reader(csvfile, delimiter=";")
        for row in cart_data:
            if row[0].lower() != "id":
                cart = {
                    "user_id": row[1],
                }
                try:
                    add_to_database(object_data=cart, model=Cart)
                except Exception as e:
                    print(e)
    pass


def tag_processing():
    with open(
        settings.CSV_ROOT + "tag.csv",
        newline="",
    ) as csvfile:
        tag_data = csv.reader(
            csvfile,
            delimiter=";",
        )
        for row in tag_data:
            if row[0].lower() != "id":
                tag = {
                    "name": row[1],
                    "color": row[2],
                }
                try:
                    add_to_database(object_data=tag, model=Tag)
                except Exception as e:
                    print(e)
    pass


def ingredient_processing():
    with open(
        settings.CSV_ROOT + "ingredients.csv",
        newline="",
    ) as csvfile:
        ingredient_data = csv.reader(csvfile, delimiter=";")
        for row in ingredient_data:
            if row[0] != "name":
                ingredient = {
                    "name": row[0],
                    "measurement_unit": row[1],
                }
                try:
                    add_to_database(object_data=ingredient, model=Ingredient)
                except Exception as e:
                    print(e)
    pass


def recipe_processing():
    with open(
        settings.CSV_ROOT + "recipe.csv",
        newline="",
    ) as csvfile:
        recipe_data = csv.reader(csvfile, delimiter=";")
        for row in recipe_data:
            if row[0].lower() != "id":
                recipe = {
                    "name": row[1],
                    "text": row[2],
                    "cooking_time": row[3],
                    "image": row[4],
                    "author_id": row[5],
                }
                try:
                    add_to_database(object_data=recipe, model=Recipe)
                except Exception as e:
                    print(e)
    pass


def cart_item_processing():
    with open(
        settings.CSV_ROOT + "cart_item.csv",
        newline="",
    ) as csvfile:
        cart_item_data = csv.reader(csvfile, delimiter=";")
        for row in cart_item_data:
            if row[0].lower() != "id":
                cart_item = {
                    "cart_id": row[1],
                    "recipe_id": row[2],
                }
                try:
                    add_to_database(object_data=cart_item, model=CartItem)
                except Exception as e:
                    print(e)
    pass


def favoriterecipe_processing():
    with open(
        settings.CSV_ROOT + "favorite_recipe.csv",
        newline="",
    ) as csvfile:
        favorite_recipe_data = csv.reader(csvfile, delimiter=";")
        for row in favorite_recipe_data:
            if row[0].lower() != "id":
                favorite_recipe = {
                    "recipe_id": row[1],
                    "user_id": row[2],
                }
                try:
                    add_to_database(
                        object_data=favorite_recipe, model=FavoriteRecipe
                    )
                except Exception as e:
                    print(e)
    pass


@transaction.atomic
def add_to_database(object_data, model):
    """Create objects in database"""
    if issubclass(model, User):
        if int(object_data.get("is_superuser")) == 1:
            model.objects.create_superuser(
                email=object_data.get("email"),
                password=object_data.get("password"),
                first_name=object_data.get("first_name"),
                last_name=object_data.get("last_name"),
                username=object_data.get("username"),
            )
            return
        model.objects.create_user(
            email=object_data.get("email"),
            password=object_data.get("password"),
            first_name=object_data.get("first_name"),
            last_name=object_data.get("last_name"),
            username=object_data.get("username"),
        )
        return
    elif issubclass(model, Recipe):
        recipe = model(
            name=object_data.get("name"),
            text=object_data.get("text"),
            cooking_time=object_data.get("cooking_time"),
            image=object_data.get("image"),
            author_id=object_data.get("author_id"),
        )
        recipe.full_clean()
        recipe.save()
        with transaction.atomic():
            create_recipe_ingredients(recipe=recipe)
            create_recipe_tags(recipe=recipe)
        return
    elif issubclass(model, CartItem):
        cart_item = model(
            cart_id=object_data.get("cart_id"),
            recipe_id=object_data.get("recipe_id"),
        )
        cart_item.full_clean()
        cart_item.save()
        return
    elif issubclass(model, FavoriteRecipe):
        favorite_recipe = model(
            recipe_id=object_data.get("recipe_id"),
            user_id=object_data.get("user_id"),
        )
        favorite_recipe.full_clean()
        favorite_recipe.save()
        return
    elif issubclass(model, Subscription):
        subscription = model(
            author_id=object_data.get("author_id"),
            user_id=object_data.get("user_id"),
        )
        subscription.full_clean()
        subscription.save()
        return
    elif issubclass(model, Tag):
        tag = model(
            name=object_data.get("name"),
            color=object_data.get("color"),
        )
        tag.full_clean()
        tag.save()
        return
    elif issubclass(model, Cart):
        cart = model(user_id=object_data.get("user_id"))
        cart.full_clean()
        cart.save()
        return
    elif issubclass(model, Ingredient):
        ingredient = model(
            name=object_data.get("name"),
            measurement_unit=object_data.get("measurement_unit"),
        )
        ingredient.full_clean()
        ingredient.save()
        return


def create_recipe_ingredients(recipe):
    with open(
        settings.CSV_ROOT + "recipeingredients.csv",
        newline="",
    ) as csvfile:
        recipe_ingredient_data = csv.reader(csvfile, delimiter=";")
        for row in recipe_ingredient_data:
            if row[0].lower() != "id":
                recipe_ingredient = {
                    "ingredient_id": row[1],
                    "recipe_id": row[2],
                    "amount": row[3],
                }
                if int(recipe_ingredient.get("recipe_id")) == recipe.id:
                    _object = RecipeIngredient(
                        ingredient_id=recipe_ingredient.get("ingredient_id"),
                        recipe_id=recipe.id,
                        amount=recipe_ingredient.get("amount"),
                    )
                    _object.full_clean()
                    _object.save()


def create_recipe_tags(recipe):
    with open(
        settings.CSV_ROOT + "recipetags.csv",
        newline="",
    ) as csvfile:
        recipe_tag_data = csv.reader(csvfile, delimiter=";")
        for row in recipe_tag_data:
            if row[0].lower() != "id":
                recipe_tag = {
                    "recipe_id": row[1],
                    "tag_id": row[2],
                }
                if int(recipe_tag.get("recipe_id")) == recipe.id:
                    _object = RecipeTag(
                        recipe_id=recipe.id, tag_id=recipe_tag.get("tag_id")
                    )
                    _object.full_clean()
                    _object.save()
