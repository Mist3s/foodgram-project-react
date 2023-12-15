from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet

from users.models import Follow, User
from .serializers import FollowSerializer


class CustomUserViewSet(UserViewSet):
    ...


class FollowListViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )

    def get_queryset(self):
        return self.request.user.follower.all()


class FollowCreateDestroyViewSet(mixins.CreateModelMixin,
                                 mixins.DestroyModelMixin,
                                 viewsets.GenericViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        user_id = get_object_or_404(
            User,
            pk=self.kwargs.get('user_id')
        )
        print(user_id)
        serializer.save(
            user=self.request.user,
            following=user_id
        )

    def get_queryset(self):
        return self.request.user.follower.all()
