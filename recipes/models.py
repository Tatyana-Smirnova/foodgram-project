from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(max_length=200)
    dimension = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Tag(models.Model):
    value = models.CharField(max_length=50, null=True)
    style = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author'
    )
    pub_date = models.DateTimeField(
        'date published',
        auto_now_add=True
    )
    title = models.CharField(max_length=200, blank=False)
    image = models.ImageField(upload_to='media/', blank=False)
    description = models.TextField(blank=False)
    ingredient = models.ManyToManyField(
        Ingredient,
        related_name='recipe_ingredient',
        through='Amount',
        through_fields=('recipe', 'ingredient')
    )
    tags = models.ManyToManyField(Tag, related_name='recipe_tag')
    cooking_time = models.IntegerField(validators=[MinValueValidator(1),
                                                   MaxValueValidator(10000)],
                                       blank=False)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Amount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_amount'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_amount',
    )
    quantity = models.FloatField(validators=[MinValueValidator(0.1),
                                             MaxValueValidator(100000)],
                                 blank=False)

    def __str__(self):
        return self.ingredient.title


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )

    def __str__(self):
        return self.recipe.title


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    def __str__(self):
        return self.user.username


class ShopList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shop_list"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop_list'
    )

    def __str__(self):
        return self.recipe.title
