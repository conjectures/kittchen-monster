from django.contrib import admin
from .models import Post, Ingredient, IngredientTable, Direction, Image, Category
# Register your models here.
from django.contrib.auth.models import User

admin.site.register(Ingredient)
admin.site.register(IngredientTable)
admin.site.register(Direction)
admin.site.register(Image)
admin.site.register(Category)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', )
    readonly_fields = ('posted_at', 'last_edited')
