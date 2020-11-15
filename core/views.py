import pdb
from core.utils.debug import debug

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, FormView
from .models import *
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.detail import SingleObjectMixin
from django.forms import inlineformset_factory, modelformset_factory
from .forms import *


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


def IngredientsAddView(request):

    if request.method == 'POST':
        form = AddPostIntermediateForm(request.POST)
        if form.is_valid():
            # process data in form.cleaned_data as required
            post = Post()
            post.title = form.cleaned_data['title']
            post.body = form.cleaned_data['body']
            post.author = request.user
            post.save()
            return HttpResponseRedirect(reverse_lazy('home'))
    else:
        form = AddPostIntermediateForm()
    return render(request, 'ingredients_form.html', {'form': form})


class RecipeAddView(CreateView):
    """
    Add recipe title only
    """
    model = Post
    template_name = 'recipe_add.html'
    form_class = PostModelForm

    @debug
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    @debug
    def get_success_url(self):
        return reverse('recipe_add_ingredients', kwargs={'pk': self.object.pk})


# View combining all components needed to add recipe
class RecipeIngredientsAddView(SingleObjectMixin, FormView):
    model = Post
    template_name = 'recipe_add_ingredients.html'
    # overwrite 'need pk' function

#    @debug
#    def get_queryset(self):
#        return Post.objects.all()

    # GET request: Render response with new Post model as context
    @debug
    def get(self, request, *args, **kwargs):
        # Post edited
        self.object = self.get_object(queryset=Post.objects.all())
        return super().get(request, *args, **kwargs)

    # Construct form, check for validity and handle accordingly
    @debug
    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Post.objects.all()) 
        return super().post(request, *args, **kwargs)

    # Get custom nested formset and pass in Post object
    @debug
    def get_form(self, form_class=None):

        return PostIngredientTableFormset(
                **self.get_form_kwargs(), instance=self.object)

    @debug
    def form_valid(self, form):
        """
        If form is valid, redirect to supplied URL
        """
        form.save()

        messages.add_message(
                self.request,
                messages.SUCCESS,
                'Changes were saved.'
                )

        return HttpResponseRedirect(self.get_success_url())

    @debug
    def get_success_url(self):
        return reverse('recipe_detail', kwargs={'pk': self.object.pk})


#     # Create formset based on parent and child model
#      IngredientsTableFormSet = inlineformset_factory(Ingredient, IngredientTable, fields=('unit', 'quantity',)(()), extra=1)
#      IngredientFormSet = modelformset_factory(Ingredient, fields=('name',))
#
#      formPost = PostModelForm(request.POST or None)
#     # Generate form and formset
#     if (new_recipe_inst is None)
#
#     if request.method == 'POST':
#         formset = IngredientFormSet(queryset=Ingredient.objects.filter(name__startswith='a'))
#
#         if formset.is_valid():
#             for instance in formset:
#                 instance.save()
#     else:
#         formset = IngredientFormSet()
#         formPost = PostModelForm()
#
#     context = {
#             'formset': formset,
#             'formPost': formPost,
#             }
#     return render(request, 'create_recipe.html', context)

#        formIngredient = AddPostIntermediateForm(request.POST)
#        formDirection = AddPostIntermediateForm(request.POST)
#        if formPost.is_valid():
#            # process data in form.cleaned_data as required
#            post = Post()
#            post.title = formPost.cleaned_data['title'=
#            post.author = request.user
#            post.save()
#            return HttpResponseRedirect(reverse_lazy('home'))
#        else:
#            print(formPost.errors)
#
#    else:
#        formPost = PostModelForm()
#    return render(request, 'create_recipe.html', {
#        'form': formPost, })
