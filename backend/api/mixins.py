from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet


class ListRetriveViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    pass


class CreateDestroyListViewSet(
    GenericViewSet, CreateModelMixin, DestroyModelMixin, ListModelMixin
):
    pass
