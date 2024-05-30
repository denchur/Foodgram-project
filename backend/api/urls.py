from django.urls import include, path, re_path
from rest_framework import routers

from api.views import (CustomUserViewSet, IngredintViewSet, RecipeViewSet,
                       TagViewSet)

app_name = 'api'

api_router_v1 = routers.DefaultRouter()
api_router_v1.register('recipes', RecipeViewSet, basename='recipe')
api_router_v1.register('tags', TagViewSet, basename='tag')
api_router_v1.register('ingredients', IngredintViewSet, basename='ingredient')
api_router_v1.register(r'users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('', include(api_router_v1.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
