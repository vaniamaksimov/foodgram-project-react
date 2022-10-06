from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .mixins import ListRetriveViewSet
from .serializers import (FavoriteRecipeSerializer, IngridientSerializer,
                          RecipeSerializer, TagSerializer,
                          UserRecipeSerializer, UserSubscriptionSerializer, RecipeCreateSerializer)
from app.models import FavoriteRecipe, Ingridient, Recipe, Tag
from cart.models import Cart, Cart_item
from core.generics import get_object_or_400
from users.models import Subscription

User = get_user_model()


class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngridientViewSet(ListRetriveViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("name",)
    search_fields = ("name",)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        _serializer = RecipeSerializer(instance=serializer.instance, context={'request': request})
        return Response(_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, id=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        if self.request.method == "POST":
            favorite, created = FavoriteRecipe.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not created:
                return Response(
                    data={"errors": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = FavoriteRecipeSerializer(
                instance=recipe, context={"request": request}
            )
            return Response(data=serializer.data)
        favorite = get_object_or_400(FavoriteRecipe, user=user, recipe=recipe)
        favorite.delete()
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, id=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        cart, created = Cart.objects.get_or_create(user=user)
        if self.request.method == "POST":
            cart_item, _created = Cart_item.objects.get_or_create(
                cart=cart, recipe=recipe
            )
            if not _created:
                return Response(
                    data={"errors": "Рецепт уже в корзине"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = UserRecipeSerializer(
                instance=cart_item.recipe, context={"request": request}
            )
            return Response(data=serializer.data)
        if self.request.method == "DELETE":
            cart_item = get_object_or_400(Cart_item, recipe=recipe, cart=cart)
            cart_item.delete()
            return Response(data=None, status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    @action(
        methods=["get"], detail=False, permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request, *args, **kwargs):
        user = self.request.user
        queryset = User.objects.filter(subscription__user=user)
        paginated_queryset = self.paginate_queryset(queryset=queryset)
        serializer = UserSubscriptionSerializer(
            paginated_queryset, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=[IsAuthenticated],
        name="subscribe",
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {"errors": "Вы не можете подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if self.request.method == "POST":
            subscription, created = Subscription.objects.get_or_create(
                user=user, author=author
            )
            if not created:
                return Response(
                    {"errors": "Вы уже подписаны на этого автора"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = User.objects.get(id=author.id)
            serializer = UserSubscriptionSerializer(
                queryset, context={"request": request}
            )
            return Response(serializer.data)
        if self.request.method == "DELETE":
            subscription = get_object_or_400(
                Subscription, user=user, author=author
            )
            subscription.delete()
            return Response(data=None, status=status.HTTP_204_NO_CONTENT)
