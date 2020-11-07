
from . import views
from django.urls import path


urlpatterns = [
        path('', views.HomeView.as_view(), name='home'),
        path('recipe/<int:pk>', views.RecipeDetailView.as_view(), name='recipe_detail'),
        ]
