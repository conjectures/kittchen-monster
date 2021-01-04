"""kittchen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views
# from django.contrib.auth.models import User
# from rest_framework import routers, serializers, viewsets


"""
    API
"""


# Serializers define the API representation
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ['url', 'username', 'email', 'is_staff']


# ViewSets define the view behavior
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


# Routers provide an easy way of automatically determining the URL conf
# router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)


urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),
    # CORE APP
    path('', include('core.urls')),
    # path('', RedirectView.as_view(url='home/', permanent=True)),
    # AUTH
    # path('accounts/', include('django.contrib.auth.urls')),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # API
    # Wire API using automatic URL routing. Additionally include login URLS for browsable API
    # path('api', include(router.urls)),
    path('api/', include('core.api.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
