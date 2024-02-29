from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.conf import settings
from recipes.models import Subscribe, Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'password',
                  'is_subscribed',
                  )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.subscriber.filter(user=user).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор новых пользователей."""

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'password',

                  )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор игредиентов в рецептах."""

    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов."""

    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='ingredient'
    )
    image = Base64ImageField(max_length=None, use_url=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('__all__')
        read_only_fields = ('id', 'author',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.shopping.filter(user=user).exists()


class CreateIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов, для создания пользователем рецепта."""

    id = serializers.IntegerField()
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.IntegerField(
        write_only=True,
        min_value=settings.MIN_COOKING_TIME_AND_AMOUNT_INGREDIENT,
        max_value=settings.MAX_COOKING_TIME_AND_AMOUNT_INGREDIENT
    )

    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = CreateIngredientSerializer(many=True)
    cooking_time = serializers.IntegerField(
        write_only=True,
        min_value=settings.MIN_COOKING_TIME_AND_AMOUNT_INGREDIENT,
        max_value=settings.MAX_COOKING_TIME_AND_AMOUNT_INGREDIENT
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        ingredients = data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredients_list.append(ingredient.get('id'))
        for ingredient in ingredients:
            if ingredients_list.count(ingredient['id']) > 1:
                dublicate = Ingredient.objects.get(
                    pk=ingredient.get('id')
                )
                raise serializers.ValidationError(
                    f'Ингредиент, {dublicate}, '
                    f'выбран более одного раза.'
                )
        return data

    def create_ingredients(self, recipe, ingredients):
        create_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(
            create_ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if 'tags' in validated_data:
            instance.tags.set(validated_data.get('tags'))
        if 'ingredients' in validated_data:
            instance.ingredients.clear()
            self.create_ingredients(
                instance, validated_data.get('ingredients')
            )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def to_representation(self, obj):
        """Возвращаем прдеставление в таком же виде, как и GET-запрос."""
        self.fields.pop('ingredients')
        representation = super().to_representation(obj)
        representation['ingredients'] = RecipeIngredientsSerializer(
            obj.ingredient.all(), many=True
        ).data
        return representation


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения информации рецепта в подписке."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения списка подписок."""

    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    email = serializers.ReadOnlyField(source='author.email')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return obj.author.subscriber.filter(user=obj.user).exists()

    def get_recipes(self, obj):
        return SubscribeRecipeSerializer(
            obj.author.recipes.all(),
            many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class SubscribeUserSerializer(serializers.ModelSerializer):
    """Сериализатор создания/отмены подписки на пользователя."""

    class Meta:
        model = Subscribe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author',),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        if data.get('user') == data.get('author'):
            raise serializers.ValidationError(
                'Вы не можете оформить подписку на себя.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeSerializer(
            instance,
            context={'request': request}
        ).data


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецептов в подписке."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
