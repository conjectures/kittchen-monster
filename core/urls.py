
from django.views.generic import RedirectView
from django.urls import path

from . import views


urlpatterns = [
        path('', RedirectView.as_view(url='home/', permanent=True)),
        path('home/', views.HomeView.as_view(), name='home'),
        path('recipe/<int:pk>', views.RecipeDetailView.as_view(), name='recipe_detail'),
        path('recipe/<int:pk>/edit/', views.RecipeUpdateView.as_view(), name='recipe_edit'),
        path('recipe/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
        path('myrecipes', views.RecipeByUserListView.as_view(), name='myrecipes'),
        path('recipe/create/', views.RecipeCreateView.as_view(), name='recipe_create'),
        path('recipe/create/<int:pk>/add/', views.RecipeAddView.as_view(), name='recipe_add'),
        path('recipe/browse/', views.RecipeBrowse.as_view(), name='recipe_browse'),
        path('category/list/', views.CategoryListView.as_view(), name='category_list'),
        path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
        path('category/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_rename'),
        path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_remove'),
        # path('recipe/add/<int:pk>/test', views.testView.as_view(), name='test_recipe_add_ingredients'),
        # path('testmodel/create/', views.TestModelCreateView.as_view(), name='test_model_create'),
        ]
