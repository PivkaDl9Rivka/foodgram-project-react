from django.urls import include, path
from rest_framework import routers
from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewset,
                    SubscribeView, SubscriptionsList, TagViewSet)

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewset, basename='recipes')

urlpatterns = [
    path(r'users/<int:user_id>/subscribe/', SubscribeView.as_view()),
    path(r'users/subscriptions/', SubscriptionsList.as_view({'get': 'list'})),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
