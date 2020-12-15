from django.shortcuts import get_object_or_404
from django.forms import ValidationError

from .models import Tag


def get_ingredients(request):
    ingredients = {}
    for key in request.POST:
        if key.startswith('nameIngredient'):
            ing_num = key[15:]
            ingredients[request.POST[key]] = request.POST[
                'valueIngredient_' + ing_num]
    for ing in ingredients:
        if float(ingredients[ing]) < 0.0:
            raise ValidationError('Значение не может быть отрицательным')
    return ingredients


def get_tags_for_edit(request):
    data = request.POST.copy()
    tags = []
    for tag in Tag.objects.all():
        value = tag.value
        if value in data and data.get(value) == 'on':
            tag = get_object_or_404(Tag, value=value)
            tags.append(tag)

    return tags


def get_dict_purchases(recipes):
    ing: dict = {}
    for recipe in recipes:
        ingredients = recipe.ingredient.values_list(
            'title', 'dimension'
        )
        amount = recipe.recipe_amount.values_list(
            'quantity', flat=True
        )

        for num in range(len(ingredients)):
            title: str = ingredients[num][0]
            dimension: str = ingredients[num][1]
            quantity: int = amount[num]
            if title in ing.keys():
                ing[title] = [ing[title][0] + quantity, dimension]
            else:
                ing[title] = [quantity, dimension]
    return ing
