from django.contrib import admin
from .models import Post, Ingredient, IngredientTable, Direction, Image, Category
# Register your models here.
from django.contrib.auth.models import User
from ordered_model.admin import OrderedModelAdmin


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', )
    readonly_fields = ('posted_at', 'last_edited')


class DirectionAdmin(OrderedModelAdmin):
    list_display = ('body', 'move_up_down_links')


admin.site.register(Ingredient)
admin.site.register(IngredientTable)
admin.site.register(Direction, DirectionAdmin)
admin.site.register(Image)
admin.site.register(Category)


