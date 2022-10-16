from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet

app_name = "api"

api_router = DefaultRouter()
api_router.register("tags", TagViewSet, basename="tags")
api_router.register("ingredients", IngredientViewSet, basename="ingredients")
api_router.register("recipes", RecipeViewSet, basename="recipes")
api_router.register("users", CustomUserViewSet, basename="users")


urlpatterns = [
    path("", include(api_router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
