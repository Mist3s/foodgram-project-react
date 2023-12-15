from django.urls import path, include, re_path
from rest_framework import routers


v1_router = routers.DefaultRouter()


urlpatterns = [
    path('', include(v1_router.urls)),
    re_path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
