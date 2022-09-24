from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from core.validators import not_me_in_username_validator


class CustomUserManager(BaseUserManager):
    def create_user(
        self, email, password, first_name, last_name, username, **extra_fields
    ):
        if not email:
            raise ValueError("Необходимо предоставить Email")
        if not password:
            raise ValueError("Необходимо предоставить пароль")
        if not first_name:
            raise ValueError("Необходимо предоставить имя")
        if not last_name:
            raise ValueError("Необходимо предоставить фамилию")
        if not username:
            raise ValueError("Необходимо предоставить никнейм")
        email = self.normalize_email(email=email)
        user = self.model(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self, email, password, first_name, last_name, username, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(
            email, password, first_name, last_name, username, **extra_fields
        )


class User(AbstractUser):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        verbose_name="Логин пользователя",
        max_length=150,
        unique=True,
        help_text=(
            "Требуется, максимум 150 символов, латиница,"
            " цифры и @/./+/-/_. Нельзя Me/mE/ME/me"
        ),
        validators=[username_validator, not_me_in_username_validator],
        error_messages={
            "unique": "Пользователь с таким логином уже существует",
        },
    )
    first_name = models.CharField(
        verbose_name="Имя", max_length=150, blank=False, null=False
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=150, blank=False, null=False
    )
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        blank=False,
        null=False,
        unique=True,
        error_messages={
            "unique": (
                "Пользователь с таким"
                "адресом электронной "
                "почты уже существует"
            )
        },
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="subscriber",
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="subscription",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"], name="unique author"
            ),
        ]

    def __str__(self):
        return f"Подписка на автора {self.author} пользователем {self.user}"
