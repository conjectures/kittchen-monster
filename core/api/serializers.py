from rest_framework import serializers
from core.models import Post, IngredientTable, Ingredient, Category


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'cooking_time')


class IngredientTableSerializer(serializers.ModelSerializer):
    ingredient = serializers.StringRelatedField()

    class Meta:
        model = IngredientTable
        exclude = ('id', 'post',)
        # fields = "__all__"


class PostDetailSerializer(serializers.ModelSerializer):
    ingredients = IngredientTableSerializer(source="items", many=True)
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = "__all__"
