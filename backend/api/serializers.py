from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.models import (FavoriteRecipe, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from users.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    '''
    Сериализатор регистрации пользователя.
    Если данные валидны, то юзер считается зарегистрирован.
    '''
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        '''
        Создает юзера с определенными данными.
        '''
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserSerializer(UserSerializer):
    '''
    Сериализатор для просмотра пользователей.
    is_subscribed - показывает есть ли подписка у пользователя
    на указанного автора.
    '''
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class FollowSerializer(CustomUserSerializer):
    """
    Возвращает пользователей, на которых подписан текущий пользователь.
    В выдачу добавляются рецепты.
    Recipes_count - Общее количество рецептов пользователя.
    """
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipe.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipe.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор отображения сведений о рецепте.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class TagSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для сведений о тэгах.
    '''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    '''
   Сериализатор для сведений об ингредиентах.
    '''
    class Meta:
        model = Ingredient
        exclude = ('quantity',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для сведений о количестве определенных ингредиентов
    в рецепте.
    '''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measure_unit = serializers.ReadOnlyField(
        source='ingredient.measure_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measure_unit')


class AddIngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для отображения добавленных ингредиентов в рецепт.
    '''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ShowRecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для отображения рецептов.
    is_favorited - показывает есть ли рецепты, находящиеся в списке избранного.
    is_in_shopping_cart - показывает есть ли рецепты,
    находящиеся в списке покупок.
    '''
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        queryset = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shop_list.filter(recipe=obj).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для избранных рецептов.
    '''

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'user', 'recipe',)

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if FavoriteRecipe.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                {
                    'status': 'Рецепт уже добвлен в избранное'
                }
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe, context=context
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для рецептов в Вашем списке покупок.
    '''

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if ShoppingList.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                {
                    'status': 'Рецепт уже добвлен в список покупок.'
                }
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe, context=context
        ).data


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления рецептов.
    """

    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def validate(self, data):
        ingredients = data['ingredients']
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    {
                        'ingredients': 'Данный ингредиент уже есть в рецепте.'
                    }
                )

            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) < 1:
                raise serializers.ValidationError(
                    {
                        'amount': 'В рецепте должен быть хотя бы 1 ингредиент.'
                    }
                )

        tags = data['tags']
        tag_list = []
        if not tags:
            raise serializers.ValidationError(
                    {
                        'tags': 'Для Вашего рецепта нужно указать тэг.'
                    }
                )

        for tag in tags:
            if tag in tag_list:
                raise serializers.ValidationError(
                    {
                        'tags': 'Данный тэг неуникален. Укажите другой.'
                    }
                )
            tag_list.append(tag)

        return data
                 

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeSerializer(instance, context=context).data

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)
