from django.contrib import admin

from .models import Cart, CartItem


class CartModelsAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user",)


class CartItemModelsAdmin(admin.ModelAdmin):
    list_display = ("cart", "recipe")
    list_filter = ("cart",)


admin.site.register(Cart, CartModelsAdmin)
admin.site.register(CartItem, CartItemModelsAdmin)
