import pdb

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from .models import Post
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from .forms import AddPostForm, AddPostModelForm


class HomeView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'recipe_list'


class RecipeDetailView(DetailView):
    model = Post
    template_name = 'recipe_detail.html'




class RecipeUpdateView(UpdateView):
    model = Post
    form_class = AddPostModelForm
    template_name = 'update_recipe_form.html'
    # empty dict to add initial data
    initial = {}
    success_url = reverse_lazy('home')
#    def get_success_url(self):
#        return reverse_lazy('recipe_details', kwargs={'pk': self.object.pk})

    def get_initial(self):
        # initialize form values here
        base_initial = super().get_initial()
        return base_initial

#    def form_valid(self, form):
#        response = super().form_valid(form)
#        form.instance.save()
#        return response


class RecipeDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    template_name = 'recipe_confirm_delete.html'


class RecipeByUserListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'recipe_list_user.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


def createRecipeView(request):
    # If POST request process the Form data
    if request.method == 'POST':
        form = AddPostModelForm(request.POST)
        if form.is_valid():
            # process data in form.cleaned_data as required
            post = Post()
            post.title = form.cleaned_data['title']
            post.body = form.cleaned_data['body']
            post.author = request.user
            post.save()
            return HttpResponseRedirect(reverse_lazy('home'))
    else:
        form = AddPostModelForm()
    return render(request, 'create_recipe_form.html', {'form': form})
