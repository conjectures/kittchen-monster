from django.db import models
from datetime import date, datetime
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


# Post
class Post(models.Model):
    title = models.CharField(max_length=100, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # delete blogs of deleted user
    ingredients = models.ManyToManyField('Ingredient', through='IngredientTable', help_text='Input ingredients', blank=True)
    body = models.TextField(max_length=1000, help_text='Recipe body')
    posted_at = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    # Return url
    def get_absolute_url(self):
        return reverse('recipe_detail', args=[str(self.id)])

    def save(self):
        self.last_edited = datetime.now()
        super().save()


class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name}"


class IngredientTable(models.Model):
    ML = 'ml'
    L = 'L'
    G = 'g'
    KG = 'Kg'
    CUP = 'cup'
    TSP = 'tsp'
    TBS = 'tbsp'
    UNIT = [
            (ML, _('ml')),
            (L, _('L')),
            (G, _('g')),
            (CUP, _('cup')),
            (TSP, _('tsp')),
            (TBS, _('tbsp')),
            ]
    unit = models.CharField(
            max_length=32,
            choices=UNIT,
            blank=True,
            )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=8, decimal_places=3)           # store as character then make into integer

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient} for {self.post.title}"

    def get_units(self):
        return self.get_unit_display()


class Direction(models.Model):
    recipe = models.ForeignKey(Post, related_name='directions', on_delete=models.CASCADE)
    position = models.IntegerField()
    body = models.CharField(max_length=100)

    def __str__(self):
        return f"Direction {self.position} for {self.recipe.title}: {self.body}"




