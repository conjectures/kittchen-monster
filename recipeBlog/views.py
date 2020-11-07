from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from .models import Post
from django.urls import reverse_lazy


class HomeView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'recipe_list'


class RecipeDetailView(DetailView):
    model = Post
    template_name = 'recipe_detail.html'


class RecipeCreateView(CreateView):
    model = Post
    fields = '__all__'


class RecipeUpdateView(UpdateView):
    model = Post
    fields = '__all__'


class RecipeDelete(DeleteView):
    model = Post
    success_url = reverse_lazy('home')
