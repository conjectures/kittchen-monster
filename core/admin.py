from django.contrib import admin
from .models import Post, Ingredient, IngredientTable, Direction
# Register your models here.
from django.contrib.auth.models import User

admin.site.register(Post)
admin.site.register(Ingredient)
admin.site.register(IngredientTable)
admin.site.register(Direction)
