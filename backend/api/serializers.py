from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Follow

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'username',
            'password',
            'first_name',
            'last_name'
        )

    def validate_username(self, username):
        if username == r'^(?i)(?!me$).*':
            raise ValidationError(
                {'username': 'Запрещенное значение для юзернейма.'},
                code=status.HTTP_400_BAD_REQUEST
            )
        return username


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('email', 'username')

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit is not None:
            limit = int(limit)
            recipes = recipes[:limit]
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CreateFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('author', 'user')

    def validate(self, attrs):
        user = attrs.get('user')
        author = attrs.get('author')
        if user == author:
            raise ValidationError(
                {'author': 'Нельзя подписаться на самого себя.'},
                code=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                {'author': 'Подписка уже существует.'},
                code=status.HTTP_400_BAD_REQUEST
            )
        return attrs

    def to_representation(self, instance):
        return FollowSerializer(
            self.instance.user,
            context={'request': self.context.get('request')}
        ).data


class AddToShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('recipe', 'user')

    def validate(self, attrs):
        recipe = attrs.get('recipe')
        user = attrs.get('user')
        if Cart.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'recipe': 'Вы уже добавляли в корзину этот рецепт.'},
                code=status.HTTP_400_BAD_REQUEST
            )
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class AddToFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def validate(self, attrs):
        recipe = attrs.get('recipe')
        user = attrs.get('user')
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'recipe': 'Вы уже добавляли в избранное этот рецепт.'},
                code=status.HTTP_400_BAD_REQUEST
            )
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'image'
        )
        read_only_fields = ('__all__',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredients_recipe'
    )
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'text',
            'cooking_time',
            'author',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart'
        )
        model = Recipe

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and user.favorites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.carts.filter(recipe=obj).exists()


class AddRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredients_recipe',
    )
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'text',
            'cooking_time',
            'author',
            'tags',
            'ingredients'
        )
        model = Recipe

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError(
                {'tags': 'Для создания рецепта нужен хотябы один тэг'},
                code=status.HTTP_400_BAD_REQUEST
            )
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {'tags': 'Теги не могут повторяться'},
                    code=status.HTTP_400_BAD_REQUEST
                )
            tags_list.append(tag)

        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                {'ingredients':
                    'Для создания рецепта нужен хотя бы один ингредиент'},
                code=status.HTTP_400_BAD_REQUEST
            )
        ingredients_list = []
        for item in ingredients:
            ingredient = item['ingredient']['id']
            if ingredient in ingredients_list:
                raise ValidationError(
                    {'ingredients': 'Ингредиенты не могут повторяться'},
                    code=status.HTTP_400_BAD_REQUEST
                )
            if int(item['amount']) <= 0:
                raise ValidationError(
                    {'amount': 'Количество ингредиента должно быть больше 0'},
                    code=status.HTTP_400_BAD_REQUEST
                )
            ingredients_list.append(ingredient)
        return ingredients

    def _create_ingredients(self, ingredients_data, recipe):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        tags = validated_data.pop('tags')
        new_ingridients = validated_data.pop('ingredients_recipe')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self._create_ingredients(new_ingridients, recipe)
        return super().update(instance, validated_data)
