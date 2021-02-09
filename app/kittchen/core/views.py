import re
from kittchen.core.utils.debug import debug
from kittchen.core.utils.multiform import *
from kittchen.core.utils.forms import parse_form_id, is_formset, is_dictionary
from .forms import *

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.forms import inlineformset_factory, modelformset_factory
from django.db.models import Q

from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView


class HomeView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'recipe_list'
    queryset = Post.objects.all()[:5]


class RecipeDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    template_name = 'recipe_confirm_delete.html'


class RecipeByUserListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'recipe_list_user.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


class RecipeCreateView(LoginRequiredMixin, CreateView):
    """
    Add recipe title only
    """
    model = Post
    template_name = 'recipe_create_form.html'
    form_class = PostTitleForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('recipe_add', kwargs={'pk': self.object.pk})


class BaseRecipeAddView(LoginRequiredMixin, SingleObjectMixin, FormView):
    """ View combining all components needed to add recipe """
    model = Post
    template_name = 'recipe_add_form.html'
    form_names = {
            'recipe': PostModelForm,
            'categories': PostCategoryForm,
            'items': PostIngredientTableForm,
            'directions': PostDirectionForm,
            'images': PostImageFormset,
            }
    form_models = {
            'recipe': Post,
            'categories': Category,
            'items': IngredientTable,
            'directions': Direction,
            'images': Image,
            }
    # instanciate form - self.object is recipe post

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = self.get_forms()
        # self.get_form_models()
        return render(request, self.template_name, context={'formset': formset, 'recipe': self.object})

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        # formset = self.get_forms(request.POST or None,  instance=self.object)
        prefix = parse_form_id(request.POST.get('action'))
        action = prefix[0]
        # Get context request context
        if "REMOVE" in prefix:
            klass = self.get_form_models([prefix[0]])[0]
            object_to_remove = klass.objects.get(id=prefix[1])
            # Try to remove realtion with recipe instance
            try:
                # Getattr used to have variable as attribute
                getattr(self.object, prefix[0]).remove(object_to_remove)
            # If removal fails, the object only has the one connection and has to be deleted
            except AttributeError:
                object_to_remove.delete()
            # Render again with new context
            return render(request, self.template_name, context={
                'formset': self.get_forms(),
                'recipe': self.object,
                })

        if action in self.get_form_prefixes():
            formset = self.get_forms(
                    request={
                        'data': request.POST or None,
                        'files': request.FILES or None,
                        }, form_names=[action])[action]
        else:
            # The 'delete' action will remove recipe instance
            if action == 'delete':
                return redirect('recipe_delete', pk=self.object.id)
            else:
                return redirect(self.object)

        # Before validation check if delete button was pressed

        # check if formset
        if self.validate_forms(formset):
            # Form or formset is valid.
            context = {'formset': self.get_forms(), 'recipe': self.object}
        else:
            # Render with errors
            context = {
                    'formset': dict(
                        {action: formset},
                        **self.get_forms(form_names=[x for x in self.get_form_prefixes() if not x == action])
                        ),
                    'recipe': self.object
                    }

        return render(request, self.template_name, context=context)

    def validate_forms(self, formset):
        # Check if dictionary
        if is_dictionary(formset):
            # validate each form / formset in dictionary
            for key, item in formset.items():
                self.validate_forms(item)
            self.all_forms_valid()
        # Validate form or formset
        else:
            if formset.is_valid():
                # Check if formset
                if is_formset(formset):
                    for form in formset:
                        if form.has_changed():
                            form.save()
                formset.save()
                return True
            # Handle errors,
            else:
                # Check if formset
                if is_formset(formset):
                    # check if form has been deleted
                    for form in formset:
                        if form.has_changed() and formset._should_delete_form(form):
                            form.instance.delete()
                            return True
                # If for loop exits or if not formset, return False to render with errors
                return False

    def all_forms_valid(self):
        return render(self.get_object())

    # Used to return prefixes of each formset
    def get_form_models(self, keys=None):
        if not keys:
            keys = [*self.form_models]
        return [self.form_models[x] for x in keys]

    def get_form_prefixes(self):
        return [*self.form_names]

    # Return a dictionary of prefixes and formset classes for a list of prefixes
    def get_form_names(self, form_names=None):
        # if no form name was given, assume all forms are needed
        if not form_names:
            form_names = [*self.form_names]
        return {x: self.form_names.get(x) for x in form_names}

    def get_forms(self, request=None, form_names=None):
        # forms = super().get_forms(form_classes)
        instance = self.get_object()
        dictionary = self.get_form_names(form_names)
        if request:
            request_data = request.get('data')
            request_files = request.get('files')
            context = {key: klass(data=request_data, files=request_files, instance=instance, prefix=key) for (key, klass) in dictionary.items()}
        else:
            context = {key: klass(instance=instance, prefix=key) for (key, klass) in dictionary.items()}
        return context

    def dispatch(self, request, *args, **kwargs):
        """ Restrict permission to non staff and non author """
        handler = super().dispatch(request, *args, **kwargs)
        user = request.user
        post = self.get_object()
        if not (post.author == user or user.is_staff):
            raise PermissionDenied
        return handler


class RecipeAddView(BaseRecipeAddView):
    template_name = 'recipe_add_form.html'

#    def get_queryset(self):
#        return super().filter(user=self.request.user)


class RecipeUpdateView(BaseRecipeAddView):
    template_name = 'recipe_add_form.html'

#    def get_queryset(self):
#        return super().filter(user=self.request.user)


class RecipeDetailView(DetailView):
    model = Post
    template_name = 'recipe_detail.html'


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'category_list'
    ordering = ['name']


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'category_create_form.html'
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse('category_list')

    def dispatch(self, request, *args, **kwargs):
        """ Restrict permission to non staff and non author """
        handler = super().dispatch(request, *args, **kwargs)
        user = request.user
        if not user.is_staff:
            raise PermissionDenied
        return handler


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'category_update_form.html'
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse('category_list')

    def dispatch(self, request, *args, **kwargs):
        """ Restrict permission to non staff and non author """
        handler = super().dispatch(request, *args, **kwargs)
        user = request.user
        if not user.is_staff:
            raise PermissionDenied
        return handler


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('category_list')
    template_name = 'category_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        """ Restrict permission to non staff and non author """
        handler = super().dispatch(request, *args, **kwargs)
        user = request.user
        if not user.is_staff:
            raise PermissionDenied
        return handler


def is_valid_queryparam(param):
    return param != '' and param is not None


class RecipeBrowse(ListView):
    model = Post
    context_object_name = 'recipe_list'
    template_name = 'recipe_browse.html'
    # paginate_by = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        self.queryset = Post.objects.all()
        return self.queryset

    def get(self, request, *args, **kwargs):
        # Load queryset if first time get is called
        if not hasattr(self, 'object_list'):
            self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # Do cheap query than load unpaginated queryset in memory
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_(f'Empty list and "{self.__class__.__name__}.allow_empty" is False '))

        # TODO: SANITIZE URL
        pattern = request.GET.get('pattern', None)
        category_list = request.GET.get('filter_by', None)
        category_list = category_list.split() if category_list is not None else []
        form = SearchForm(request.GET or None, filter_tags=category_list)
        # category_list = Category.objects.get(pk=category_list)
        qs = self.filter_queryset(category_list=category_list, pattern=pattern)

        context = self.get_context_data(recipe_list=qs, form=form, filter_list=Category.objects.all(), active_list=category_list)
        return self.render_to_response(context)

    def filter_queryset(self, qs=None, category_list=None, pattern=None):
        if not qs:
            qs = self.object_list
        # if category_list:
        #     # append to self.category_list
        #     self.category_list = self.category_list + [category_list]
        # If ocategory list conatins ids then filter
        if len(category_list):
            qs = qs.filter(categories__name__in=category_list).distinct()
        if is_valid_queryparam(pattern):
            qs = qs.filter(title__icontains=pattern)

        return qs
