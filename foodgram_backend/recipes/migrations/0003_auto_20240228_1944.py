# Generated by Django 3.2.3 on 2024-02-28 16:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20240227_0402'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('id',), 'verbose_name': 'Объект избранного', 'verbose_name_plural': 'Объекты избранного'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'ordering': ('id',), 'verbose_name': 'Ингредиент в рецепте', 'verbose_name_plural': 'Ингредиенты в рецептах'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'ordering': ('id',), 'verbose_name': 'Рецепт для покупок', 'verbose_name_plural': 'Рецепты для покупок'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время приготовления минимум 1 минута'), django.core.validators.MaxValueValidator(32000, message='Время приготовления максимум 32000 минуты')], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество не меньше чем 1'), django.core.validators.MaxValueValidator(32000, message='Максимальное количество не более 32000')], verbose_name='Количество'),
        ),
    ]
