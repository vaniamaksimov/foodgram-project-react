from rest_framework import serializers
from django.conf import settings

from app.models import Ingridient, Tag
from users.models import Subscription

from django.contrib.auth import get_user_model
User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tag


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "measurement_unit")
        model = Ingridient
