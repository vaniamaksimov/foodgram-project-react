# Generated by Django 4.1.1 on 2022-09-24 08:27

import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                error_messages={
                    "unique": "Пользователь с таким логином уже существует"
                },
                help_text="Требуется, максимум 150 символов, латиница, цифры и @/./+/-/_. Нельзя Me/mE/ME/me",
                max_length=150,
                unique=True,
                validators=[
                    django.contrib.auth.validators.UnicodeUsernameValidator(),
                    django.core.validators.RegexValidator(
                        message="Нельзя указывать Me/mE/ME/me в качестве логина",
                        regex="^(?!me$)^[\\w.@+-]+$",
                    ),
                ],
                verbose_name="Логин пользователя",
            ),
        ),
    ]
