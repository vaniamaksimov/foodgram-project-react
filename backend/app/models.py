import textwrap

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from pytils.translit import slugify


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название тега",
        max_length=200,
        blank=False,
        null=False,
        unique=True,
        db_index=True,
    )
    color = models.CharField(
        verbose_name="Код цвета",
        max_length=7,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message=("Введите валидное" "значение в формате HEX"),
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
            "Укажите уникальный адрес для страницы"
            " задачи. Используйте только латиницу, "
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
            self.name, settings.LENGTH_OF_STRING, settings.END_OF_STRING
        )


class Ingridient(models.Model):
    name = models.CharField(
        verbose_name="Название ингридиента",
        max_length=200,
        blank=False,
        null=False,
        unique=True,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=50,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ["name"]

    def __str__(self):
        return textwrap.shorten(
            self.name, settings.LENGTH_OF_STRING, settings.END_OF_STRING
        )


class Recipe(models.Model):
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=200,
        blank=False,
        null=False,
        unique=True,
        db_index=True,
    )
    text = models.TextField(
        verbose_name="Текст рецепта", blank=False, null=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        blank=False,
        null=False,
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
        blank=False,
        through="RecipeTag",
    )
    created_at = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="recipes",
        on_delete=models.CASCADE,
        blank=False,
    )
    ingridients = models.ManyToManyField(
        Ingridient,
        related_name="recipes",
        verbose_name="Ингридиенты рецепта",
        blank=False,
        through="RecipeIngridient",
    )
    image = models.ImageField(
        verbose_name="Изображение рецепта",
        upload_to="images/",
        blank=False,
        null=False,
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
            self.name, settings.LENGTH_OF_STRING, settings.END_OF_STRING
        )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)


class RecipeIngridient(models.Model):
    ingridient = models.ForeignKey(Ingridient, on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        blank=False,
        null=False,
        validators=[
            MinValueValidator(
                limit_value=0, message="Количество не может быть меньше 0"
            )
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ingridient", "recipe"],
                name="unique_ingridient_for_recipe",
            )
        ]

    def __str__(self):
        return (
            f"В рецепте {self.ingridient} используется "
            f"ингридиент {self.ingridient} в количестве {self.quantity}"
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
        ordering = ["user"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unice_favorite_recipe"
            )
        ]

    def __str__(self):
        return f"Избранный рецепт {self.recipe} пользователя {self.name}"
