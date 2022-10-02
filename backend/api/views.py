from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.conf import settings
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from .mixins import ListRetriveViewSet, CreateDestroyListViewSet
from .serializers import (
    IngridientSerializer,
    TagSerializer,
    RecipeSerializer,
    UserSubscriptionSerializer,
)
from app.models import Ingridient, Tag, Recipe
from users.models import Subscription
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework import status

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
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


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
            subscription = Subscription.objects.filter(
                user=user, author=author
            )
            if not subscription.exists():
                return Response(
                    {"errors": "Вы не были подписаны на данного автора"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription.delete()
            return Response(data=None, status=status.HTTP_204_NO_CONTENT)
