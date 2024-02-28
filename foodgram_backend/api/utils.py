from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def post(request, pk, model, serializer):
    recipe = get_object_or_404(Recipe, pk=pk)
    if model.objects.filter(user=request.user, recipe=recipe).exists():
        return Response(
            {'Notification': 'Рецепт уже есть в избранном/списке покупок'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    model.objects.get_or_create(user=request.user, recipe=recipe)
    data = serializer(recipe).data
    return Response(data, status=status.HTTP_201_CREATED)


def delete(request, pk, models):
    obj = get_object_or_404(Recipe, pk=pk)
    needed_recipe = models.objects.filter(recipe=obj, user=request.user)
    if not needed_recipe.exists():
        return Response(
            {'Notification':
                f'Вы не добавляли рецепт {obj}.'}
        )
    needed_recipe.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
