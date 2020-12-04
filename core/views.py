import re
from core.utils.debug import debug
from core.utils.multiform import *
from core.utils.forms import get_name_with_flag, get_id_with_flag, parse_form_id, is_formset, is_dictionary

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, FormView
from .models import *
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.detail import SingleObjectMixin
from django.forms import inlineformset_factory, modelformset_factory
from .forms import *
# from .forms import IngredientModelFormset


from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView


class HomeView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'recipe_list'


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
    form_class = PostModelForm

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
            'ingredients': PostIngredientTableFormset,
            'directions': PostDirectionFormset,
            'images': PostImageFormset,
            }
    form_models = {
            'recipe': Post,
            'ingredients': IngredientTable,
            'directions': Direction,
            'images': Image,
            }
    # instanciate form - self.object is recipe post

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = self.get_forms()
        self.get_form_models()
        return render(request, self.template_name, context={'formset': formset, 'recipe': self.object})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # formset = self.get_forms(request.POST or None,  instance=self.object)
        prefix = parse_form_id(request.POST.get('action'))
        action = prefix[0]
        if action in self.get_form_prefixes():
            formset = self.get_forms(
                    request={
                        'data': request.POST or None,
                        'files': request.FILES or None,
                        }, form_names=[action])[action]
        # Else, get all forms (?) TODO
        else:
            if action == 'delete':
                return redirect('recipe_delete', pk=self.object.id)
            else:
                return redirect(self.object)

        # check if formset
        if self.validate_forms(formset):
            # Form or formset is valid.
            context = {'formset': self.get_forms(), 'recipe': self.object}
        else:
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
            # TODO: check if return value necessary
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
    template_name = 'recipe_edit_form.html'

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


# class RecipeUpdateView(UpdateView):
#     model = Post
#     form_class = AddPostModelFormcac
#     template_name = 'recipe_add_form.html'
#     # empty dict to add initial data
#     # initial = {}
#     success_url = reverse_lazy('home')
#    def get_success_url(self):
#        return reverse_lazy('recipe_details', kwargs={'pk': self.object.pk})

    # def get_initial(self):
    #     # initialize form values here
    #     base_initial = super().get_initial()
    #     return base_initial

#    def form_valid(self, form):
#        response = super().form_valid(form)
#        form.instance.save()
#        return response

# class TestModelCreateView(CreateView):
#     model = TestModel
#     template_name = 'test.html'
#     # fields = '__all__'
#     success_url = reverse_lazy('home')
#     form_class = TestForm




"""

                    TESTING

"""


# View combining all components needed to add recipe
class RecipeAddIngredientsView(SingleObjectMixin, FormView):
    model = Post
    template_name = 'test_recipe_add_ingredients.html'
    formsets = {
            'recipe': PostModelForm,
            'item': IngredientModelFormset,
            'table': PostIngredientTableFormset,
            }
    # overwrite 'need pk' function

#    @debug
#    def get_queryset(self):
#        return Post.objects.all()

    # GET request: Render response with new Post model as context
    @debug
    def get(self, request, *args, **kwargs):
        # Post edited
        self.object = self.get_object()
        forms = self.get_form()
        # print(f'get object: {self.object}')
        return render(request, self.template_name, context={'forms': forms, 'recipe': self.object})

    # Construct form, check for validity and handle accordingly
    @debug
    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        print(request.POST)
        print(self.get_form_kwargs())

        action = request.POST.get('action')
        form_id = get_id_with_flag(action)
        form_name = get_name_with_flag(action)
        # form_prefixes = self._get_prefixes()
        forms = self.get_form()

        # Find individual or group submit
        if form_name in forms.keys():
            # self._process_individual_form(form_name, form_id)
            form = IngredientModelFormset(request.POST or None, prefix='%item%')
            print(form)
            print(f"Validating {form_name} with id {form_id}")

            if form.is_valid():
                print("~~~~\nFORM IS VALID\n~~~~")
                return redirect('/home')
            else:
                print("~~~~\nNOT VALID\n~~~~")
                forms['item'] = form
                return render(request, self.template_name, context={'forms': forms, 'recipe': self.object})
        #process individual
        #process group
        # get_form_kwargs required (to get POST info)
        # return super().post(request, *args, **kwargs)

    # Get custom nested formset and pass in Post object
    def _get_prefixes(self):
        return self.formsets.keys()


    @debug
    def get_form(self, form_class=None):
        args = self.get_form_kwargs()
        # surround with '%' flag
        prefixes = [f'%{x}%' for x in self._get_prefixes()]
        # prefixes = [x for x in self._get_prefixes()]

        # TODO: 'pythonify - get names from self.formsests dictionary'
        formPost = PostModelForm(instance=self.object, prefix=prefixes[0])
        formIngredients = IngredientModelFormset(queryset=Ingredient.objects.filter(ingredienttable__post__id=self.object.id).order_by('ingredienttable'), prefix=prefixes[1])
        formPostIngredientTable = PostIngredientTableFormset(instance=self.object, prefix=prefixes[2])

        forms = {'recipe': formPost, 'item': formIngredients, 'table': formPostIngredientTable}

        return forms

#        return PostIngredientTableFormset( **self.get_form_kwargs(), instance=self.object)

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
#    def _create_form(self, form_name, klass, *args, **kwargs):
#        form_kwargs = self.get_form_kwargs(form_name)
#        form_create_method = 'create_%s_form' % form_name
#        if
#        print(f'Form kewyord arguments: {form_kwargs')
#        print(f'Form create methods: {form_create_method}')
#
#        pass
   #@debug


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
   #@debug
   #def get_form(self, form_class=None):
   #    return testModelForm(**self.get_form_kwargs(), instance=self.object)


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
