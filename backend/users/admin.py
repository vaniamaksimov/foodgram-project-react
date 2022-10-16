from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class usermodelsAdmin(UserAdmin):
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "email",
        "username",
    )


class subscriptionmodelsAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("user",)
    list_filter = ("user", "author")


admin.site.register(User, usermodelsAdmin)
admin.site.register(Subscription, subscriptionmodelsAdmin)
