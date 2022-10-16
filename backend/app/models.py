import textwrap

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from pytils.translit import slugify


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название тега",
        max_length=200,
        unique=True,
        db_index=True,
        help_text="Название тега",
    )
    color = models.CharField(
        verbose_name="Код цвета",
        max_length=7,
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message=("Введите валидное значение в формате HEX"),
            )
        ],
        help_text="Цветовой HEX-код (например, #49B64E)",
    )
    slug = models.SlugField(
        verbose_name="Адрес",
        max_length=200,
        unique=True,
        blank=True,
        help_text=(
            "Укажите уникальный адрес для страницы. "
            "Используйте только латиницу, "
            "цифры, дефисы и знаки подчёркивания,"
            " или оставьте полe пустым, "
            "адрес присвоится автоматически"
        ),
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Тэги"

    def save(self, *args, **kwargs):
        self.color = self.color.upper()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return textwrap.shorten(
            text=self.name,
            width=settings.LENGTH_OF_STRING,
            placeholder=settings.END_OF_STRING,
        )


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингридиента",
        max_length=200,
        unique=False,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=50,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "name",
                    "measurement_unit",
                ),
                name="unique_ingredient_unit",
            ),
        ]

    def __str__(self):
        return textwrap.shorten(
            text=self.name,
            width=settings.LENGTH_OF_STRING,
            placeholder=settings.END_OF_STRING,
        )


class Recipe(models.Model):
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=200,
        unique=True,
        db_index=True,
    )
    text = models.TextField(
        verbose_name="Текст рецепта", blank=False, null=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(
                limit_value=1,
                message="Время приготовления не может быть меньше 1",
            )
        ],
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Тэги рецепта",
        through="RecipeTag",
    )
    created_at = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="recipes",
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        verbose_name="Ингридиенты рецепта",
        through="RecipeIngredient",
    )
    image = models.ImageField(
        verbose_name="Изображение рецепта",
        upload_to="images/",
        default=None,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "author"], name="unique_recipes_for_author"
            ),
        ]

    def __str__(self):
        return textwrap.shorten(
            text=self.name,
            width=settings.LENGTH_OF_STRING,
            placeholder=settings.END_OF_STRING,
        )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.PROTECT,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "tag"],
                name="unique_tag_for_recipe",
            )
        ]


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(
                limit_value=0.1, message="Количество не может быть меньше 0"
            )
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="unique_ingredient_for_recipe",
            )
        ]

    def __str__(self):
        return (
            f"В рецепте {self.ingredient.name} используется "
            f"ингридиент {self.ingredient.name} в количестве {self.amount} {self.ingredient.measurement_unit}."
        )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ("user",)
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "user",
                    "recipe",
                ),
                name="unice_favorite_recipe",
            )
        ]

    def __str__(self):
        return f"Избранный рецепт {self.recipe.name} пользователя {self.user.get_full_name()}"
