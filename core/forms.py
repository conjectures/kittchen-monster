import time
from .utils.debug import debug
from django import forms
# from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import *
from .utils.forms import is_empty_form, clean_string, move_to_next_if_exists, parse_form_id
from django.forms.models import BaseInlineFormSet, inlineformset_factory, modelformset_factory, ModelMultipleChoiceField, ModelChoiceField


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', )
        widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control'})
                }

    @debug
    def clean_name(self, *args, **kwargs):
        name = clean_string(self.cleaned_data.get('name'))
        try:
            model_instance = Category.objects.get(name=name)
        except type(self.instance).DoesNotExist:
            return name
        if model_instance.id != self.instance.id:
            raise ValidationError(_(f"The recipe name '{name}' already exists"))
        else:
            return name


class PostTitleForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title',)
        widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control'})
                }

    def clean_title(self, *args, **kwargs):
        title = clean_string(self.cleaned_data.get("title"))
        try:
            model_instance = Post.objects.get(title=title)
        except type(self.instance).DoesNotExist:
            return title
        if model_instance.id != self.instance.id:
            raise ValidationError(_(f"The recipe name '{title}'' already exists"))
        else:
            return title


class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'cooking_time', 'servings', )
        widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control'}),
                'cooking_time': forms.NumberInput(attrs={'class': 'form-control'}),
                'servings': forms.NumberInput(attrs={'class': 'form-control'}),
                }

    def clean_title(self, *args, **kwargs):
        title = clean_string(self.cleaned_data.get("title"))
        try:
            model_instance = Post.objects.get(title=title)
        except type(self.instance).DoesNotExist:
            return title
        if model_instance.id != self.instance.id:
            raise ValidationError(_(f"The recipe name '{title}'' already exists"))
        else:
            return title


class ImageField(forms.ClearableFileInput):
    clear_checkbox_label = _('')
    initial_text = _('')
    input_text = _('')
    template_name = 'widgets/image_input_clearable.html'


class ImageForm(forms.ModelForm):
    image = forms.ImageField(
            label=_('Image'),
            required=False,
            error_messages={'invalid': ("Image files only")},
            widget=ImageField,
            )

    class Meta:
        model = Image
        fields = ('image', )


class ImageFormset(BaseInlineFormSet):
    """ Base formset for adding images """

    def clean(self, *args, **kwargs):
        # check if any form should be deleted:
        for form in self.forms:
            if self._should_delete_form(form):
                print("FORM SHOULD BE DELETED")
        super().clean(*args, **kwargs)

    def _should_delete_form(self, form):
        """ Check if DELETE button was pressed """
        if form.cleaned_data.get(forms.formsets.DELETION_FIELD_NAME):
            return True
        action = parse_form_id(self.data.get('action'))

        if 'DELETE' in action:
            # Get current form id:
            form_id = parse_form_id(form.prefix)[1]
            # If action id matches current form id form should be deleted
            if form_id == action[1]:
                return True
        return False


PostImageFormset = inlineformset_factory(
        Post,
        Image,
        fields=('image',),
        formset=ImageFormset,
        form=ImageForm,
        extra=1,
        # can_delete=True,
        )


class CategoryInputField(ModelMultipleChoiceField):
    widget = forms.TextInput(attrs={'class': 'form-control'})

    @debug
    def clean(self, value, *args, **kwargs):
        print(f"{self=}")
        if value is not None:
            print(f"{value.split(',')=}")
            value = [clean_string(item.strip()) for item in value.split(',')]
            print(f"{value=}")
        return super().clean(value)


class PostCategoryForm(forms.ModelForm):
    "Model form for Recipes"
    categories = CategoryInputField(
            required=False,
            queryset=Category.objects.filter(),
            to_field_name='name',
            initial='',
            )

    def __init__(self, *args, **kwargs):

        instance = kwargs.get('instance', None)
        kwargs.update(initial={
            'categories': '',
            })
        super().__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ('categories', )

    # return entered categories with already selected
    def clean_categories(self, *args, **kwargs):
        cleaned_data = self.cleaned_data.get('categories', None)
        existing_categories = self.instance.categories.all()
        # Combine existing categories with cleaned data
        return existing_categories | cleaned_data


class IngredientInputField(ModelChoiceField):
    widget = forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingredient',
        })

    def clean(self, value, *args, **kwargs):
        value = clean_string(value)
        # If no value, raise validation error.
        if not value:
            print("Value not entered")
            raise ValidationError(self.error_messages['required'], code='required')
        # Else try to return queryset of ingredient, or create
        # TODO: Check if value exists as plural/ singular
        value, is_new = self.queryset.get_or_create(**{'name': value})
        return super().clean(value)


class PostIngredientTableForm(forms.ModelForm):
    ingredient = IngredientInputField(
            required=False,
            queryset=Ingredient.objects.filter(),
            to_field_name='name',
            )
    post = ModelChoiceField(
            required=False,
            queryset=Post.objects.filter(),
            )
    quantity = forms.DecimalField(
            required=False,
            widget=forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantity',
                })
            )

    class Meta:
        model = IngredientTable
        fields = ('ingredient', 'unit', 'quantity')
        widgets = {
                'unit': forms.Select(attrs={
                    'class': 'form-control',
                    'placehodler': 'unit'
                    # 'style': 'width: 40%',
                    }),
                }

    def __init__(self, *args, **kwargs):
        self.dependent = kwargs.pop('instance', None)
        kwargs.update({'instance': None})
        opts = self._meta
        super().__init__(*args, **kwargs)

    @debug
    def save(self, commit=True):
        ingredient_table_instance = super().save(commit=False)
        ingredient_table_instance.post = self.dependent
        ingredient_table_instance.save()
        return ingredient_table_instance


class PostDirectionForm(forms.ModelForm):
    """ Directions form """
    recipe = ModelChoiceField(
            required=False,
            queryset=Post.objects.filter(),
            )
    position = forms.IntegerField(
            required=False,
            widget=forms.NumberInput(attrs={
                'class': 'form-control',
                }),
            )
    body = forms.CharField(
            widget=forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'style': 'resize:none',
                }),
            required=False,
            )

    # position = forms.NumberInput()

    def __init__(self, *args, **kwargs):
        self.dependent = kwargs.pop('instance', None)
        kwargs.update({'instance': None})
        opts = self._meta
        super().__init__(*args, **kwargs)

    def clean_body(self, *args, **kwargs):
        value = self.cleaned_data.get('body', None)
        if value:
            value = clean_string(value)
            self.cleaned_data['body'] = value
        else:
            raise ValidationError("This field is required.")
        return value

    def save(self, commit=True):
        # check if position was given
        dir_instance = super().save(commit=False)
        dir_instance.recipe = self.dependent
        dir_instance.save()
        position = self.cleaned_data.get('position', None)
        if position:
            dir_instance.to(position-1)
        else:
            dir_instance.bottom()
        return dir_instance

    class Meta:
        model = Direction
        fields = ('position', 'body', )


class SearchForm(forms.Form):
    pattern = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Search...',
                }),
            )
    filter_by = forms.ModelChoiceField(
            required=False,
            queryset=Category.objects.filter(),
            to_field_name='name',
            widget=forms.Select(attrs={
                'class': 'form-control',
                'style': 'display: flex;'
                }),
            )

    def __init__(self, *args, filter_tags=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_tags = filter_tags
        if filter_tags:
            self.fields['filter_by'].queryset = Category.objects.all().exclude(name__in=filter_tags)

