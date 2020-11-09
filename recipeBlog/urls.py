
from . import views
from django.urls import path


urlpatterns = [
        path('', views.HomeView.as_view(), name='home'),
        path('recipe/<int:pk>', views.RecipeDetailView.as_view(), name='recipe_detail'),
        path('recipe/create/', views.RecipeCreateView.as_view(), name='recipe_create'),
        path('recipe/<int:pk>/edit/', views.RecipeUpdateView.as_view(), name='recipe_edit'),
        path('recipe/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
        path('myrecipes', views.RecipeByUserListView.as_view(), name='myrecipes'),
        ]
