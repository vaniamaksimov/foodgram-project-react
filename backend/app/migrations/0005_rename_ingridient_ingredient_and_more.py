# Generated by Django 4.1.1 on 2022-10-12 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_alter_recipeingridient_amount"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Ingridient",
            new_name="Ingredient",
        ),
        migrations.RenameModel(
            old_name="RecipeIngridient",
            new_name="RecipeIngredient",
        ),
        migrations.RemoveConstraint(
            model_name="recipeingredient",
            name="unique_ingridient_for_recipe",
        ),
        migrations.RenameField(
            model_name="recipeingredient",
            old_name="ingridient",
            new_name="ingredient",
        ),
        migrations.RemoveField(
            model_name="recipe",
            name="ingridients",
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                related_name="recipes",
                through="app.RecipeIngredient",
                to="app.ingredient",
                verbose_name="Ингридиенты рецепта",
            ),
        ),
        migrations.AddConstraint(
            model_name="recipeingredient",
            constraint=models.UniqueConstraint(
                fields=("ingredient", "recipe"),
                name="unique_ingredient_for_recipe",
            ),
        ),
    ]
