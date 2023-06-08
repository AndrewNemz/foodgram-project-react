from django_filters import rest_framework as f
from rest_framework.filters import SearchFilter
from recipes.models import Recipe


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(f.FilterSet):
    """
    Кастомный фильтр для модели рецептов.
    """
    tags = f.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    is_favorited = f.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = f.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shop_list__user=user)
        return queryset
