from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_recipe, name="new_recipe"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("profile/<str:username>/<int:recipe_id>/", views.recipe_view,
         name="recipe_view"),
    path("profile/<str:username>/<int:recipe_id>/edit/", views.recipe_edit,
         name="recipe_edit"),
    path("profile/<str:username>/<int:recipe_id>/delete/", views.recipe_delete,
         name="recipe_delete"),
    path("ingredients/", views.ingredients, name="ingredients"),
    path("favorites/", views.favorites, name="favorites"),
    path("change_favorites/<int:recipe_id>/", views.change_favorites,
         name="change_favorites"),
    path("follow/", views.my_follow, name="my_follow"),
    path("subscriptions/<int:author_id>/", views.subscriptions,
         name="subscriptions"),
    path("shop_list/", views.shop_list, name="shop_list"),
    path("purchases/", views.get_purchases, name="get_purchases"),
    path("purchases/<int:recipe_id>/", views.purchases, name="purchases")
]
