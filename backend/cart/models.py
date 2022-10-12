from django.conf import settings
from django.db import models

from app.models import Recipe


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        blank=False,
        null=False,
        unique=True,
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"


class Cart_item(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="cart_items",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="cart_items",
    )

    class Meta:
        verbose_name = "Рецепт корзины"
        verbose_name_plural = "Рецепты корзины"
        ordering = ["cart"]
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "recipe"], name="unique_recipe_for_cart"
            ),
        ]

    def __str__(self):
        return f"Рецепт {self.recipe} в корзине пользователя {self.cart.user.username}"
