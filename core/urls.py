
from . import views
from django.urls import path


urlpatterns = [
        path('', views.HomeView.as_view(), name='home'),
        path('recipe/<int:pk>', views.RecipeDetailView.as_view(), name='recipe_detail'),
        path('recipe/create/', views.createRecipeView, name='recipe_create'),
        path('recipe/<int:pk>/edit/', views.RecipeUpdateView.as_view(), name='recipe_edit'),
        path('recipe/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
        path('myrecipes', views.RecipeByUserListView.as_view(), name='myrecipes'),
        path('ingredients/add/', views.IngredientsAddView, name='ingredients_add'),
        path('recipe/add/', views.RecipeAddView.as_view(), name='recipe_add'),
        path('recipe/add/<int:pk>', views.RecipeIngredientsAddView.as_view(), name='recipe_add_ingredients'),
        path('recipe/add/<int:pk>/test', views.testView.as_view(), name='test_recipe_add_ingredients'),
        ]
