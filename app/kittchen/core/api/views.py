# REST FRAMEWORK
from rest_framework import permissions, status, generics
# from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from rest_framework.generics import get_object_or_404
from rest_framework import permissions

from kittchen.core.models import Post
from kittchen.core.api.pagination import ListPagination
from kittchen.core.api.serializers import (PostListSerializer,
                                  PostDetailSerializer)


# @api_view(['GET'])
# @permission_classes((permissions.AllowAny,))
# def apiOverview(request):
#     api_urls = {
#             'List': '/recipe-list/',
#             'Detail View': '/recipe-detail/<str:pk>/',
#             }
#     return Response(api_urls)


class ApiOverview(APIView):
    # throttle_classes = [UserRateThrottle]

    def get(self, request, format=None):
        content = {
                'status': 'request was premitted',
                'List': '/recipe-list/',
                'Detail View': '/recipe-detail/<str:pk>/',
                }
        return Response(content)


# class RecipeListAPIView(APIView):
class RecipeListAPIView(generics.ListAPIView):

    queryset = Post.objects.all().order_by("-id")
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ListPagination
#     def get(self, request):
#         recipes = Post.objects.filter()
#         serializer = PostListSerializer(recipes, many=True)
#         return Response(serializer.data)


class RecipeDetailAPIView(generics.RetrieveAPIView):

    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

#     def get_object(self, pk):
#         recipe = get_object_or_404(Post, pk=pk)
#         return recipe

#     def get(self, request, pk):
#         recipe = self.get_object(pk)
#         serializer = PostDetailSerializer(recipe)
#         return Response(serializer.data)
