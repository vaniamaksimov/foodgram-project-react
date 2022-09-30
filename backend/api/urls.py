from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngridientViewSet, RecipeViewSet

app_name = "api"

api_router = DefaultRouter()
api_router.register("tags", TagViewSet, basename="tags")
api_router.register("ingridients", IngridientViewSet, basename="ingridients")
api_router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path("", include(api_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include("djoser.urls.authtoken")),
]
