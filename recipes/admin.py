from django.contrib import admin

from .models import (Amount, Favorite, Ingredient, Recipe, ShopList,
                     Subscription, Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'show_favorites',)
    list_filter = ('author', 'title', 'tags',)

    def show_favorites(self, obj):
        result = Favorite.objects.filter(recipe=obj).count()
        return result

    show_favorites.short_description = "Favorite"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'dimension',)
    list_filter = ('title',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


class TagAdmin(admin.ModelAdmin):
    list_display = ('value', 'style', 'name')


admin.site.register(Amount)
admin.site.register(Favorite)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShopList)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Tag, TagAdmin)
