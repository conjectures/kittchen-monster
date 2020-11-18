from .utils.debug import debug
from django import forms
# from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import *
from .utils.forms import is_empty_form, is_form_persisted
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
                    'margin': '0',
                    'padding': '0',
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


class AddPostIntermediateForm(forms.ModelForm):
    custom = forms.ModelChoiceField(queryset=Direction.objects.all(), empty_label="Custom Field")

    class Meta:
        model = Post
        fields = ['title', 'ingredients', 'body', 'custom']


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


class IngredientTableModelForm(forms.ModelForm):
    class Meta:
        model = IngredientTable
        fields = ('unit', 'quantity')
        widgets = {
                'unit': forms.Select(attrs={
                    'class': 'form-control',
                    'style': 'width: 40%',
                    }),
                'quantity': forms.NumberInput(attrs={
                    'class': 'form-control',
                    'style': 'width: 50%',
                    })
                }


class DirectionForm(forms.ModelForm):
    class Meta:
        model = Direction
        fields = '__all__'


class IngredientWithTableForm(BaseInlineFormSet):
    """
    Base formset with ingredient and ingredietntable forms
    """

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.nested = IngredientModelForm()
        pass

#    def is_adding_nested_inlines_to_empty_form(self, form):
#        pass

    def is_valid(self):
        for form in self.forms:
            if hasattr(form, 'nested'):
                result = form.nested.is_valid()

        return super().is_valid() and result

    def clean(self):
        for form in self.forms:
            if not hasattr(form, 'nested') or self._should_delete_form(form):
                continue
            form.nested.clean()
        super().clean()

    def save(self, commit=True):

        for form in self.forms:
            print("TEST SAVE METHOD ~~~~")
            print(form)
            if hasattr(form, 'nested'):
                form.nested.save(commit=True)
        return


PostIngredientTableFormset = inlineformset_factory(
        Post,
        IngredientTable,
        fields=('unit', 'quantity'),
        form=IngredientTableModelForm,
        extra=1,
        can_delete=False,
        )


class BaseRecipeWithIngredientTableFormset(BaseInlineFormSet):
    """
    Base formset for editing Ingredient Tables belonging to Recipes
    """

    def add_fields(self, form, index):
        super().add_fields(form, index)
        # save the formset for a book's images in the nested property
        form.nested = IngredientFormset(instance=form.instance,
                                        data=form.data if form.is_bound else None,
                                        files=form.files if form.is_bound else None,
                                        # add custom prefix
                                        prefix=f"ingredienttable-{form.prefix}-{IngredientFormset.get_default_prefix()}")

    def is_adding_nested_inlines_to_empty_form(self, form):
        """
        are data added in nested inline forms to a form without data?
        """
        if not hasattr(form, 'nested'):
            # form without children (leaf)
            return False
        if is_form_persisted(form):
            # Editing (and not adding) current form
            return False
        if not is_empty_form(form):
            # Form has errors or contains valid data
            return False
        # All inline forms that aren't being deleted:
        non_deleted_forms = set(form.nested.forms).difference(set(form.nested.deleted_forms))
        # If above checks failed, the form is empty. Return True if there is any data inside nested
        return any(not is_empty_form(nested_form) for nested_form in non_deleted_forms)

    def is_valid(self):
        """
        Also validate nested formsets
        """
        result = super().is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result

    def clean(self):
        """
        If a parent form has no data, but nedted forms do,
        an error should return because parent can't be saved.
        """
        super.clean()
        for form in self.forms:
            # check if it has child or is marked for deletion
            if not hasattr(form, 'nested') or self._should_delete_form(form):
                continue
            if self._is_adding_nested_inlines_to_empty_form(form):
                form.add_error(
                        field=None,
                        error=_('You are adding ingredients to a book that does not exist yet'))

    def save(self, commit=True):
        """
        Also save nested formsets
        """
        result = super.save(commit=commit)
        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)
        return result
#PostIngredientTableFormset = inlineformset_factory(
#        Post,
#        IngredientTable,
#        formset=BaseRecipeWithIngredientTableFormset,
#        fields=('qu'),
#        extra=1
#        )

#class AddPostForm(forms.Form):
#    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
#    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
