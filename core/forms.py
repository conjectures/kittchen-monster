import time
from .utils.debug import debug
from django import forms
# from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import *
from .utils.forms import is_empty_form, clean_string, move_to_next_if_exists
from django.forms.models import BaseInlineFormSet, inlineformset_factory, modelformset_factory


IngredientFormset = inlineformset_factory(
        Ingredient,
        IngredientTable,
        fields=('ingredient', 'unit', 'quantity'),
        extra=1)


class IngredientModelForm(forms.ModelForm):

    class Meta:
        model = Ingredient
        fields = ('name',)
        widgets = {
                'name': forms.TextInput(attrs={
                    'class': 'form-control',
                    'width': '100%',
                    })
                }

    def clean_name(self, *args, **kwargs):
        name = self.cleaned_data.get("name")
        if Ingredient.objects.filter(name=name).exists():
            raise ValidationError(_(f"The ingredient name '{name}'' already exists"))

        return name


IngredientModelFormset = modelformset_factory(Ingredient, form=IngredientModelForm, fields=('name',))


class AddPostModelForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'body']
        widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control'}),
                'body': forms.Textarea(attrs={'class': 'form-control'})
                }


#class AddPostIntermediateForm(forms.ModelForm):
#    custom = forms.ModelChoiceField(queryset=Direction.objects.all(), empty_label="Custom Field")
#
#    class Meta:
#        model = Post
#        fields = ['title', 'ingredients', 'body', 'custom']


class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title',)
        widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control'})
                }

    @debug
    def clean_title(self, *args, **kwargs):
        title = self.cleaned_data.get("title")
        if Post.objects.filter(title=title).exists():
            raise ValidationError(_(f"The recipe name '{title}'' already exists"))

        return title


# Overwrite of TextInput form field render
class IngredientInput(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        # TODO: softcode object model
        if type(value) == int:
            new = Ingredient.objects.get(pk=value).name if value else ''
            value = new
        return super().render(name, value, attrs)


class IngredientField(forms.ModelChoiceField):
    # update initial value with instance name (for has_changed to work)
    # edit `to_python` function to fix validation

    # @debug
    def prepare_value(self, value):
        return super().prepare_value(value)

    @debug
    def to_python(self, value):
        # Change field key to name
        self.to_field_name = "name"
        # Transform name to id
        if value in self.empty_values:
            return None
        try:
            # Get selection key field
            key = self.to_field_name or 'pk'
            # Check if value is of model type
            if isinstance(value, self.queryset.model):
                # get id value from model
                value = getattr(value, key)
            # Get instance of object with value as key
            if type(value) == str:
                value, is_new = self.queryset.get_or_create(**{key: clean_string(value)})
        except (ValueError, TypeError, ):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        except (self.queryset.model.DoesNotExist):
            raise ValidationError("Choice does not exist", code='invalid_choice')
        return value

    def has_changed(self, initial, data):
        # Hasnt changed if field is disabled
        if self.disabled:
            return False
        # Check if initial is empty
        initial_value = initial if initial is not None else ''
        # Check if initial is int
        if type(initial_value) == int:
            try:
                # Find object in database else ignore
                initial_value = self.queryset.model.objects.get(pk=initial_value).name
            except (self.queryset.model.DoesNotExist):
                pass
        # chack if data is empty
        data_value = data if data is not None else ''
        # return true if data not equal with initial
        return str(self.prepare_value(initial_value)) != str(data_value)


class IngredientTableForm(forms.ModelForm):
    class Meta:
        model = IngredientTable
        fields = ('ingredient', 'unit', 'quantity')
        field_classes = {
                'ingredient': IngredientField,
                }
        widgets = {
                'ingredient': IngredientInput(attrs={
                     'class': 'form-control',
                        }),
                'unit': forms.Select(attrs={
                    'class': 'form-control',
                    'style': 'width: 40%',
                    }),
                'quantity': forms.NumberInput(attrs={
                    'class': 'form-control',
                    'style': 'width: 50%',
                    })
                }

    def clean_ingredient(self):
        ingredient = self.cleaned_data.get("ingredient")
        ingredient.name = clean_string(ingredient.name)
        return ingredient

    def is_valid(self, *args, **kwargs):
        print("IN INGREDIENTTABLEMODELFORM IS VALID METHOD")
        return super().is_valid(*args, **kwargs)


class IngredientTableFormset(BaseInlineFormSet):
    """
    Base formset with ingredient and ingredietntable forms
    """

    def _should_delete_form(self, form):
        """
        Return whether the form should be deleted
        """
        if form.cleaned_data.get(forms.formsets.DELETION_FIELD_NAME):
            return True
        # Delete form if it was previously filled (and saved) and is now empty
#        if hasattr(form, 'id'):
        if ('id' in form.cleaned_data) and (form.cleaned_data['id'] is not None):
            if form.has_changed() and (not ('ingredient' in form.cleaned_data)):
                return True
        return False

    def clean(self, *args, **kwargs):
        """ Run custom validation checks on formset level """
        # queryset model: ingredientTable
        items = []
        # Check if two forms contain same ingredient
        for form in self.forms:
            # check if form is being deleted
            if self._should_delete_form(form):
                continue
            item = form.cleaned_data.get('ingredient')
            if item in items:
                print(f"{item} appears twice")
                raise ValidationError(_("Ingredients must be different"))
            items.append(item)
            print(items)
        # No need to check if there are errors
        # if any(self.errors):
        #     return


class DirectionForm(forms.ModelForm):
    class Meta:
        model = Direction
        fields = ('position', 'body', )
        widgets = {
                'position': forms.TextInput(attrs={
                     'class': 'form-control',
                     'style': 'width: 3em',
                        }),
                'body': forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'style': 'resize:none',
                    }),
                }

    def clean_body(self):
        return clean_string(self.cleaned_data.get('body'))


class DirectionFormset(BaseInlineFormSet):
    """
    Base formset for direction forms
    """

    def __iter__(self):
        """ Custom iterating method to overwrite formset display order """
        return iter(
                sorted(
                    self.forms,
                    key=lambda form:
                        # if position is defined then return it, otherwise return very large number
                        form['position'].value() if type(form['position'].value()) == int else 99))

    def __getitem__(self, index):
        return list(self)[index]

    def get_ordering_widget(self):
        return forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 4em',
            })

    def clean(self):
        """ Clean method by providing index to new form if it doesn't exist """
        # Set position as largest than previous if position field is empty
        previous_position = 0
        positions = {}
        # Iterate through forms and check their order
        for form in self.forms:
            if self._should_delete_form(form) or self._is_empty_form(form):
                continue

            if 'position' in form.cleaned_data and form.cleaned_data['position'] is not None:
                current = form.cleaned_data.get('position')
            else:
                # Change cleaned data and form instance data before
                current = previous_position + 1
                form.cleaned_data['position'] = current
                form.instance.position = current

            previous_position = current

    # TODO restructure ordering if form is deleted
    def save(self, *args, **kwargs):
        """ Save method by fixing ordering of each instance / form """
        positions = {}
        current = 1
        # Iterate through valid forms
        for form in self.forms:
            if self._should_delete_form(form) or self._is_empty_form(form):
                continue
            current = form.cleaned_data.get('position')
            if current:
                # Recursive function that places forms in dictionary with keys according 
                # to their order and shifts to next available if new is introduced
                move_to_next_if_exists(positions, current, form)
        # Iterate through dictionary and apply changes to order
        for key, form in positions.items():
            form.instance.position = key
            form.save()
        return super().save(*args, **kwargs)

    def _should_delete_form(self, form):
        """ Return whether the form should be deleted """
        if form.cleaned_data.get(forms.formsets.DELETION_FIELD_NAME):
            return True
        # Delete form if it was previously filled (and saved) and is now empty
        if ('id' in form.cleaned_data) and (form.cleaned_data['id'] is not None):
            if form.has_changed() and (not ('body' in form.cleaned_data)):
                return True
        return False

    def _is_empty_form(self, form):
        """
        Formset form is empty if no instance yet and body field is empty.
        In formset class as it needs access to 'cleaned_data' from formset
        """
        if not form.instance.id and not form.cleaned_data.get('body'):
            return True
        return False


PostIngredientTableFormset = inlineformset_factory(
        Post,
        IngredientTable,
        fields=('ingredient', 'unit', 'quantity'),
        form=IngredientTableForm,
        formset=IngredientTableFormset,
        extra=1,
        can_delete=False,
        )

PostDirectionFormset = inlineformset_factory(
        Post,
        Direction,
        fields=('position', 'body'),
        formset=DirectionFormset,
        form=DirectionForm,
        extra=1,
        can_delete=False,
        # can_order=True,
        )

# class BaseRecipeWithIngredientTableFormset(BaseInlineFormSet):
#     """
#     Base formset for editing Ingredient Tables belonging to Recipes
#     """
# 
#     def add_fields(self, form, index):
#         super().add_fields(form, index)
#         # save the formset for a book's images in the nested property
#         form.nested = IngredientFormset(instance=form.instance,
#                                         data=form.data if form.is_bound else None,
#                                         files=form.files if form.is_bound else None,
#                                         # add custom prefix
#                                         prefix=f"ingredienttable-{form.prefix}-{IngredientFormset.get_default_prefix()}")
# 
#     def is_adding_nested_inlines_to_empty_form(self, form):
#         """
#         are data added in nested inline forms to a form without data?
#         """
#         if not hasattr(form, 'nested'):
#             # form without children (leaf)
#             return False
#         if is_form_persisted(form):
#             # Editing (and not adding) current form
#             return False
#         if not is_empty_form(form):
#             # Form has errors or contains valid data
#             return False
#         # All inline forms that aren't being deleted:
#         non_deleted_forms = set(form.nested.forms).difference(set(form.nested.deleted_forms))
#         # If above checks failed, the form is empty. Return True if there is any data inside nested
#         return any(not is_empty_form(nested_form) for nested_form in non_deleted_forms)
# 
#     def is_valid(self):
#         """
#         Also validate nested formsets
#         """
#         result = super().is_valid()
#         if self.is_bound:
#             for form in self.forms:
#                 if hasattr(form, 'nested'):
#                     result = result and form.nested.is_valid()
#         return result
# 
#     def clean(self):
#         """
#         If a parent form has no data, but nedted forms do,
#         an error should return because parent can't be saved.
#         """
#         super.clean()
#         for form in self.forms:
#             # check if it has child or is marked for deletion
#             if not hasattr(form, 'nested') or self._should_delete_form(form):
#                 continue
#             if self._is_adding_nested_inlines_to_empty_form(form):
#                 form.add_error(
#                         field=None,
#                         error=_('You are adding ingredients to a book that does not exist yet'))
# 
#     def save(self, commit=True):
#         """
#         Also save nested formsets
#         """
#         result = super.save(commit=commit)
#         for form in self.forms:
#             if hasattr(form, 'nested'):
#                 if not self._should_delete_form(form):
#                     form.nested.save(commit=commit)
#         return result
