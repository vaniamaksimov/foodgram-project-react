from django.contrib import admin

from .models import Cart, Cart_item


class cartmodelsAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user",)


class cartitemmodelsAdmin(admin.ModelAdmin):
    list_display = ("cart", "recipe")
    list_filter = ("cart",)


admin.site.register(Cart, cartmodelsAdmin)
admin.site.register(Cart_item, cartitemmodelsAdmin)
