from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post


class HomeView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'recipe_list'


class RecipeDetailView(DetailView):
    model = Post
    template_name = 'recipe_detail.html'
