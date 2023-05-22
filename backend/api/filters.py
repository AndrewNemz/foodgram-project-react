from django_filters import rest_framework as f

from recipes.models import Ingredient, Recipe


class IngredientFilter(f.FilterSet):
    '''
    Кастомный фильтр для модели ингредиентов.
    Поиск по имени.
    '''
    name = f.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(f.FilterSet):
    """
    Кастомный фильтр для модели рецептов.
    """
    tags = f.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='icontains',
    )
    is_favorited = f.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_list = f.BooleanFilter(
        method='filter_is_in_shopping_list'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_list')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_list(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_list__user=user)
        return queryset
