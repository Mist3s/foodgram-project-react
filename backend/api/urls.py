from django.urls import path, include, re_path
from rest_framework import routers

from .views import FollowListViewSet, FollowCreateDestroyViewSet, CustomUserViewSet

v1_router = routers.DefaultRouter()
v1_router.register(r'users/subscriptions', FollowListViewSet)
v1_router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    FollowCreateDestroyViewSet
)
# v1_router.register(r'users', CustomUserViewSet)


urlpatterns = [
    path('', include(v1_router.urls)),
    re_path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
