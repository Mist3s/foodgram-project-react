from django.urls import path, include, re_path
from rest_framework import routers

from .views import TagViewSet, IngredientViewSet


v1_router = routers.DefaultRouter()
v1_router.register(r'tags', TagViewSet)
v1_router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(v1_router.urls)),
    re_path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
