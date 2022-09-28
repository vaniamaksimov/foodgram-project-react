from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from .mixins import ListRetriveViewSet, CreateDestroyListViewSet
from .serializers import IngridientSerializer, TagSerializer
from app.models import Ingridient, Tag
from users.models import Subscription


class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngridientViewSet(ListRetriveViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)
