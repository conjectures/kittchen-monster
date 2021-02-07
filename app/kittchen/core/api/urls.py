from django.urls import path, include
from rest_framework import routers, serializers, viewsets
# from django.contrib.auth import views
from kittchen.core.api import views

urlpatterns = [
        # path('', include(router.urls)),
        # path('', views.ApiOverview.as_view(), name='api_overview'),
        path('recipe-list/', views.RecipeListAPIView.as_view(), name='api_recipe_list'),
        path('recipe-detail/<int:pk>/', views.RecipeDetailAPIView.as_view(), name='api_recipe_detail'),

        ]
