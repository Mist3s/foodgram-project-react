from djoser.serializers import UserSerializer
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from users.models import User, Follow


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

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

    def get_is_subscribed(self, obj: User) -> bool:
        user = self.context.get("request").user
        if user.is_anonymous or (user == obj):
            return False
        return # user.following.filter(author=obj).exists()


class Follow2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = (
            'user',
            'following',
        )


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    following = CustomUserSerializer(
        # slug_field='username',
        default=User.objects.all(),
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'user',
            'following',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following']
            )
        ]

    def validate_following(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Попытка подписаться на самого себя.'
            )
        return value


