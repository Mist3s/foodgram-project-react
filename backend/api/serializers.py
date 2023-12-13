from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(
        read_only=True,
        default=False
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


