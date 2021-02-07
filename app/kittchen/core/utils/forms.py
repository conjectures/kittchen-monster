import re


# Source: https://github.com/philgyford/django-nested-inline-formsets-example/blob/main/publishing/utils/forms.py
def is_empty_form(form):
    """
    Considered empty if it passes validation but
    doesn't have data
    """
    if form.is_valid() and not form.cleaned_data:
        return True
    else:
        # form has errors(isn't valid) or
        # it doesn't have errors and contains data
        return False


def is_form_persisted(form):
    """
    Does model have a model instance attached and is not being added?
    """
    if form.instance and not form.instance.__state.adding:
        return True
    else:
        # Either form has no instance attached
        # or it has instance that is being added
        return False


def get_name_with_flag(string, flag=None):
    return re.findall(r"\%(\w*)\%", string)[0]


def get_id_with_flag(string, flag=None):
    return re.findall(r"-(\d*)-", string)[0]


# Returns clean name
def clean_string(name):
    return name.rstrip().capitalize()


# Return string split in dashes or underscores
def parse_form_id(string):
    return re.split('-|_', string)

# def clean_form_id(string, pattern=None):
#     pattern = "(\w+)(?=-)*" if pattern is None else pattern
#     return re.match(pattern, string).group()


# Reassign objects based on integer key
def move_to_next_if_exists(dli, key, obj):
    prevobj = dli.get(key)
    if prevobj:
        move_to_next_if_exists(dli, key+1, prevobj)
    dli.update({key: obj})


def is_formset(x):
    return hasattr(x, 'management_form')


def is_dictionary(x):
    if type(x) is dict:
        return True
    else:
        return False
