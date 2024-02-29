from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/images',
    )
    text = models.TextField(verbose_name='Текст рецепта',)
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        through='RecipeIngredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                settings.MIN_COOKING_TIME_AND_AMOUNT_INGREDIENT,
                message='Время приготовления минимум 1 минута'
            ),
            MaxValueValidator(
                settings.MAX_COOKING_TIME_AND_AMOUNT_INGREDIENT,
                message='Время приготовления максимум 32000 минуты'
            )
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                settings.MIN_COOKING_TIME_AND_AMOUNT_INGREDIENT,
                message='Минимальное количество не меньше чем 1'
            ),
            MaxValueValidator(
                settings.MAX_COOKING_TIME_AND_AMOUNT_INGREDIENT,
                message='Максимальное количество не более 32000'
            )
        ],
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='author',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_subscribe',
            ),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь добавивший рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorites',
            ),
        ]
        verbose_name = 'Объект избранного'
        verbose_name_plural = 'Объекты избранного'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь, добавивший рецепт для покупки',
        on_delete=models.CASCADE,
        related_name='shopping',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт для покупки',
        on_delete=models.CASCADE,
        related_name='shopping',
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shopping_cart',
            ),
        ]
        verbose_name = 'Рецепт для покупок'
        verbose_name_plural = 'Рецепты для покупок'
