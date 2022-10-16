from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class UserModelsAdmin(UserAdmin):
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "email",
        "username",
    )


class SubscriptionModelsAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("user",)
    list_filter = ("user", "author")


admin.site.register(User, UserModelsAdmin)
admin.site.register(Subscription, SubscriptionModelsAdmin)
