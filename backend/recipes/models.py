from django.core import validators
from django.db import models

from users.models import User


class Ingredient(models.Model):
    '''
    Модель для ингредиентов.
    '''
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=256,
    )
    quantity = models.CharField(
        verbose_name='Количество',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Игредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    '''
    Модель для тегов.
    Цвет тэгов обязательно в HEX формате.
    '''
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=200,
    )
    color = models.CharField(
        verbose_name='Цвет HEX формата',
        unique=True,
        max_length=7,
        validators=[
            validators.RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX.'
            )
        ]
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=200,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''
    Модель для рецептов.
    Время приготовления блюда не меньше 1 минуты.
    '''
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipe',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Имя рецепта',
    )
    image = models.ImageField(
        'Фотография блюда',
        upload_to='recipes/',
        null=True,
        blank=True,
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг рецепта',
        related_name='recipe',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления рецепта',
        validators=[validators.MinValueValidator(
            1, message='Нельзя приготовить шедевер меньше,чем за 1 минутy!'
        )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    '''
    Модель для ингредиентов, из которых состоит определенный рецепт.
    Минимальное количество ингредиентов в рецепте - 1.
    '''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиенты',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингрединетов',
        validators=[validators.MinValueValidator(
            1, message='Минимальное количество ингредиента - 1',
        )
        ]
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='unique_ingredient',
            ),
        )
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']

    def __str__(self):
        return self.ingredient.name


class Follow(models.Model):
    '''
    Модель для подписки на авторов.
    '''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписаля на автора {self.author}'


class FavoriteRecipe(models.Model):
    '''
    Модель для добавления рецептов в избранное.
    '''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            ),
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingList(models.Model):
    '''
    Модель для шоп-листа для скачивания в формате  TXT/PDF/CSV.
    '''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shop_list',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop_list',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoplist'
            ),
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список для скачивания'
