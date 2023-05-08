from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet,
    FollowListView,
    FollowViewSet,
    TagsViewSet,
    IngredientsViewSet,
    RecipeViewSet
)


app_name = 'api'


router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('tags', TagsViewSet, basename='tags')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'users/subscriptions/',
        FollowListView.as_view(),
        name='subscribers'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        FollowViewSet.as_view(),
        name='subscribe'
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
