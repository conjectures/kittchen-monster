import re
from core.utils.debug import debug
from core.utils.multiform import *
from core.utils.forms import get_name_with_flag, get_id_with_flag

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
from .forms import IngredientModelFormset


from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView


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
            #klass = self.formsets.get(form_name)
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


class testView(SingleObjectMixin, FormView):
    model = Post
    template_name = 'test.html'
    form_names = {
            'ingredients': PostIngredientTableFormset,
            'directions': PostDirectionFormset,
            }
    # instanciate form - self.object is recipe post

    @debug
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = self.get_forms()
        return render(request, self.template_name, context={'formset': formset, 'recipe': self.object})

    @debug
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # formset = self.get_forms(request.POST or None,  instance=self.object)
        action = request.POST.get('action')
        print(f"SELF OBJECT: {self.object}")
        print(f"ACTION:  {action}")
        # form_id = get_id_with_flag(action)
        # Check which form was submitted (or all)

        if action in self.get_form_prefixes():
            formset = self.get_forms(request=(request.POST or None), form_names=[action])[action]
            print("Action was in ")
            if formset.is_valid():
                # checking formset validity also checks individual form validity
                for form in formset:
                    if form.has_changed():
                        # if direction, save order as position
                        form.save()
                formset.save()
                return render(request, self.template_name, context={'formset': self.get_forms(), 'recipe': self.object})

            else:
                # if formset['action'].errors
                for form in formset:
                    if form.has_changed() and formset._should_delete_form(form):
                        print("SHOULD DELETE FORM")
                        print(form.cleaned_data)
                        form.instance.delete()
                        formset = self.get_forms()
                        return render(request, self.template_name, context={'formset': formset, 'recipe': self.object})

                # formset.errors = formset_errors
                # formset.non_form_errors = formset_non_form_errors
                print("RENDER WITH ERROR")
                # formset = self.get_forms(instance=self.object, )

                context = {
                        'formset': dict(
                            {action: formset},
                            **self.get_forms(form_names=[x for x in self.get_form_prefixes() if not x == action])
                            ),
                        'recipe': self.object
                        }
                print(context)
                return render(request, self.template_name, context)

            # return render(request, self.template_name, context={'formset': formset, 'recipe': self.object})

#        erforms = [v for i, v in enumerate(form.errors) if v ]
#        print(f"Forms with errors: {erforms}")

#        if form.is_valid():
#            print("IS VALID")
#            pass
#        else:
#            print("NOT VALID")
#            pass
#            # Form invalid
        # validate form
        # Find individual or group submit
        # if form_name in forms.keys():
    # Used to return prefixes of each formset
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
        print("IN GET FORM METHOD")
        instance = self.get_object()
        dictionary = self.get_form_names(form_names)
        print(dictionary)
        if request:
            context = {key: klass(request, instance=instance, prefix=key) for (key, klass) in dictionary.items()}
        else:
            context = {key: klass(instance=instance, prefix=key) for (key, klass) in dictionary.items()}

        print(context)
        # ingredientFormset = PostIngredientTableFormset(*args, **kwargs, prefix='ingredients')
        # directionFormset = PostDirectionFormset(*args, **kwargs, prefix='directions')
        # context = {
        #         'ingredients': ingredientFormset,
        #         'directions': directionFormset,
        #         }
        # print(cont)
        # print()
        # print(context)
        # print("END GET FORMS")

        return context


#    def _create_form(self, form_name, klass, *args, **kwargs):
#        form_kwargs = self.get_form_kwargs(form_name)
#        form_create_method = 'create_%s_form' % form_name
#        if
#        print(f'Form kewyord arguments: {form_kwargs')
#        print(f'Form create methods: {form_create_method}')
#
#        pass
   #@debug

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
