import csv
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .forms import RecipeCreateForm, RecipeForm
from .models import (Amount, Favorite, Ingredient, Recipe, ShopList,
                     Subscription, Tag, User)
from .utils import get_ingredients, get_tags_for_edit, get_dict_purchases


def index(request):
    tags_list = request.GET.getlist('filters')

    if tags_list:
        recipe_list = Recipe.objects.filter(
            tags__value__in=tags_list
        ).select_related(
            'author'
        ).prefetch_related(
            'tags'
        ).distinct()
    else:
        recipe_list = Recipe.objects.all().select_related(
            'author'
        ).prefetch_related(
            'tags'
        ).distinct()

    paginator = Paginator(recipe_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html', {
        'paginator': paginator,
        'page': page,
        'tags_list': tags_list,
    })


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    tags_list = request.GET.getlist('filters')
    if tags_list:
        recipes_profile = Recipe.objects.filter(
            author=profile, tags__value__in=tags_list
        ).select_related(
            'author'
        ).prefetch_related(
            'tags'
        ).distinct()
    else:
        recipes_profile = Recipe.objects.filter(
            author=profile
        ).select_related(
            'author'
        ).prefetch_related(
            'tags'
        ).distinct()

    paginator = Paginator(recipes_profile, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "authorRecipe.html", {
        'paginator': paginator,
        'page': page,
        'profile': profile,
        'tags_list': tags_list,
    })


def recipe_view(request, username, recipe_id):
    profile = get_object_or_404(User, username=username)
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    return render(request, 'singlePage.html', {
        'recipe': recipe,
        'profile': profile,
    })


def new_recipe(request):
    if request.method == "POST":
        form = RecipeCreateForm(request.POST, files=request.FILES or None)
        ingredients = get_ingredients(request)
        tags = get_tags_for_edit(request)
        if not tags:
            form.add_error(None, 'Добавьте теги, это поле обязательно.')
        if not ingredients:
            form.add_error(None, 'Добавьте ингредиенты из предложенных.')
        for title, _ in ingredients.items():
            if not Ingredient.objects.filter(title=title).exists():
                form.add_error(None, f'Ингредиент {title} отсутствует в базе.')

        if form.is_valid():
            my_recipe = form.save(commit=False)
            my_recipe.author = request.user
            my_recipe.save()

            for title, quantity in ingredients.items():
                ingredient = Ingredient.objects.get(title=title)
                amount = Amount(
                    recipe=my_recipe,
                    ingredient=ingredient,
                    quantity=quantity
                )
                amount.save()
            my_recipe.tags.set(tags)

            return redirect(
                'recipe_view',
                recipe_id=my_recipe.id,
                username=request.user.username
            )
    else:
        form = RecipeCreateForm()

    return render(request, "formRecipe.html", {'form': form})


def ingredients(request):
    text = request.GET['query']
    ingredients = Ingredient.objects.filter(
        title__istartswith=text
    ).values('title', 'dimension')
    ingredients_list = list(ingredients)
    return JsonResponse(ingredients_list, safe=False)


@login_required
def recipe_edit(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    author = get_object_or_404(User, id=recipe.author_id)
    recipe_tags = recipe.tags.values_list('value', flat=True)

    if request.user != author:
        return redirect(
            "recipe_view",
            username=username,
            recipe_id=recipe_id
        )

    if request.method == 'POST':
        form = RecipeForm(
            request.POST,
            files=request.FILES or None,
            instance=recipe
        )
        ingredients = get_ingredients(request)
        new_tags = get_tags_for_edit(request)
        if not new_tags:
            form.add_error(None, 'Добавьте теги, это поле обязательно.')
        if not ingredients:
            form.add_error(None, 'Добавьте ингредиенты из предложенных.')
        for title, _ in ingredients.items():
            if not Ingredient.objects.filter(title=title).exists():
                form.add_error(None, f'Ингредиент {title} отсутствует в базе.')

        if form.is_valid():
            my_recipe = form.save(commit=False)
            my_recipe.author = request.user
            my_recipe.save()
            my_recipe.recipe_amount.all().delete()

            for title, quantity in ingredients.items():
                ingredient = Ingredient.objects.get(title=title)
                amount = Amount(
                    recipe=my_recipe,
                    ingredient=ingredient,
                    quantity=quantity
                )
                amount.save()

            my_recipe.tags.set(new_tags)

            return redirect(
                'recipe_view',
                recipe_id=recipe.id,
                username=request.user.username
            )
    else:
        form = RecipeForm(instance=recipe)
    return render(request, "formChangeRecipe.html", {
        'form': form,
        'recipe': recipe,
        'recipe_tags': recipe_tags,
    })


@login_required
def recipe_delete(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    author = get_object_or_404(User, id=recipe.author_id)

    if request.user != author:
        return redirect(
            "recipe",
            username=username,
            recipe_id=recipe_id
        )

    recipe.delete()
    return redirect("profile", username=username)


@login_required
def favorites(request):
    tags_list = request.GET.getlist('filters')

    if tags_list == []:
        tags_list = [i.value for i in Tag.objects.all()]

    recipe_list = Recipe.objects.filter(
        favorite_recipes__user=request.user
    ).filter(
        tags__value__in=tags_list
    ).distinct()
    paginator = Paginator(recipe_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "favorites.html", {
        'paginator': paginator,
        'page': page,
        'tags_list': tags_list,
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def change_favorites(request, recipe_id):
    if request.method == "POST":
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(
            Recipe, pk=recipe_id
        )
        obj, created = Favorite.objects.get_or_create(
            user=request.user, recipe=recipe
        )

        if not created:
            return JsonResponse({'success': False})
        return JsonResponse({'success': True})

    elif request.method == "DELETE":
        recipe = get_object_or_404(
            Recipe, pk=recipe_id
        )
        removed = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

        if removed:
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})


@login_required
def shop_list(request):
    if request.GET:
        recipe_id = request.GET.get('recipe_id')
        ShopList.objects.get(
            recipe__id=recipe_id
        ).delete()
    purchases = Recipe.objects.filter(shop_list__user=request.user)

    return render(request, "shopList.html", {
        'purchases': purchases})


@login_required
def get_purchases(request):
    recipes = Recipe.objects.filter(
        shop_list__user=request.user
    )
    ing = get_dict_purchases(recipes)
    response = HttpResponse(content_type='txt/csv')
    response['Content-Disposition'] = 'attachment; filename="shop_list.txt"'
    writer = csv.writer(response)
    for key, value in ing.items():
        writer.writerow([f'{key} ({value[1]}) - {value[0]}'])
    return response


@login_required
@require_http_methods(["POST", "DELETE"])
def purchases(request, recipe_id):
    if request.method == "POST":
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        obj, created = ShopList.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:
            return JsonResponse({'success': False})
        return JsonResponse({'success': True})

    elif request.method == "DELETE":
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        removed = ShopList.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if removed:
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})


@login_required
@require_http_methods(["POST", "DELETE"])
def subscriptions(request, author_id):
    if request.method == "POST":
        author_id = json.loads(request.body).get('id')
        author = get_object_or_404(User, id=author_id)
        obj, created = Subscription.objects.get_or_create(
            user=request.user, author=author
        )
        if request.user == author or not created:
            return JsonResponse({'success': False})
        return JsonResponse({'success': True})

    elif request.method == "DELETE":
        author = get_object_or_404(User, id=author_id)
        removed = Subscription.objects.filter(
            user=request.user, author=author
        ).delete()
        if removed:
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})


@login_required
def my_follow(request):
    subscriptions = User.objects.filter(
        following__user=request.user
    ).annotate(
        recipe_count=Count(
            'recipe_author'
        )
    )
    recipe: dict = {}

    for sub in subscriptions:
        recipe[sub] = Recipe.objects.filter(
            author=sub
        )[:3]

    paginator = Paginator(subscriptions, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'myFollow.html', {
        'paginator': paginator,
        'page': page,
        'recipe': recipe,
    })


def page_not_found(request, exception):
    return render(request, 'misc/404.html',
                  {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html',
                  {'path': request.path}, status=500)
